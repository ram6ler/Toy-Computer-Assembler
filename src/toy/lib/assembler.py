from dataclasses import dataclass
from re import compile, match

from .exception import ToyException


def pat(s: str) -> str:
    match s:
        case "op":
            return r" *([a-zA-Z]*) *"
        case "register":
            return r" *%([0-9A-Fa-f]) *"
        case "value":
            return r" *([0-9A-Fa-fox]+) *"
        case "label":
            return r" *([a-z][a-z0-9_]*) *"
        case "at_address":
            return r" *\[" + pat("value") + r"\] *"
        case "at_label":
            return r" *\[" + pat("label") + r"\] *"
        case "at_register":
            return r" *\[" + pat("register") + r"\] *"
    raise NotImplementedError()


op_map = {
    "add": 0x1,
    "sub": 0x2,
    "and": 0x3,
    "xor": 0x4,
    "lsh": 0x5,
    "rsh": 0x6,
}

expressions = {
    # Assembly
    "label": compile(f"^{pat("label")}: *$"),
    "halt": compile(r"^halt$"),
    "not d t": compile(f"^not{pat("register") * 2}$"),
    "not d v": compile(f"^not{pat("register")}{pat("value")}$"),
    "op d s t": compile(f"^{pat("op")}{pat("register") * 3}"),
    "op d s v": compile(f"^{pat("op")}{pat("register") * 2}{pat("value")}$"),
    "op d s": compile(f"^{pat("op")}{pat("register") * 2}"),
    "op d v": compile(f"^{pat("op")}{pat("register")}{pat("value")}$"),
    "load d v": compile(f"^ld{pat("register")}{pat("value")}$"),
    "load d l": compile(f"^ld{pat("register")}{pat("label")}$"),
    "load d a": compile(f"^ld{pat("register")}{pat("at_address")}$"),
    "load d la": compile(f"^ld{pat("register")}{pat("at_label")}$"),
    "load d p": compile(f"^ld{pat("register")}{pat("at_register")}$"),
    "store d la": compile(f"^st{pat("at_address")}{pat("register")}$"),
    "store p s": compile(f"^st{pat("at_register")}{pat("register")}$"),
    "store la s": compile(f"^st{pat("at_label")}{pat("register")}$"),
    "move d s": compile(f"^mv{pat("register") * 2}$"),
    "jz d a": compile(f"^jz{pat("register")}{pat("value")}$"),
    "jz d l": compile(f"^jz{pat("register")}{pat("label")}$"),
    "jp d a": compile(f"^jp{pat("register")}{pat("value")}$"),
    "jp d l": compile(f"^jp{pat("register")}{pat("label")}$"),
    "jmp a": compile(f"^jmp{pat("value")}$"),
    "jmp l": compile(f"^jmp{pat("label")}$"),
    "call d a": compile(f"^call{pat("register")}{pat("value")}$"),
    "call d l": compile(f"^call{pat("register")}{pat("label")}$"),
    "ret d": compile(f"^ret{pat("register")}$"),
    # Special
    ".main": compile(r"^\.main$"),
    ".word": compile(r"^\.word$"),
    ".dump": compile(r"^\.dump$"),
    ".line": compile(r"^\.line$"),
    ".state": compile(r"^\.state$"),
    ".data": compile(r"^\.data *(.*)$"),
    ".ascii": compile(r'^\.ascii *"([^"]*)" *$'),
    ".char": compile(r"^\.char" + pat("register") + "$"),
    ".bin": compile(r"\.bin" + pat("register") + "$"),
    ".oct": compile(r"^\.oct" + pat("register") + "$"),
    ".den": compile(r"^\.den" + pat("register") + "$"),
    ".hex": compile(r"^\.hex" + pat("register") + "$"),
    ".pattern": compile(r"^\.pattern" + pat("register") + "$"),
    ".input": compile(r"^\.input" + pat("register") + "$"),
    ".string": compile(r"^\.string" + pat("register") + "$"),
    ".rand": compile(r"^\.rand" + pat("register") + "$"),
}


def store_word_to(d: int, value: int) -> list[int]:
    s, t = (value & 0xFF00) >> 8, value & 0x00FF
    return [
        # R[d] <- s
        0x7000 | (d << 8) | s,
        # R[F] <- 8
        0x7F08,
        # R[d] <- R[d] << R[F]
        0x500F | (d << 8) | (d << 4),
        # R[F] <- t
        0x7F00 | t,
        # R[d] <- R[d] + R[F]
        0x100F | (d << 8) | (d << 4),
    ]


def parse_register(r: str) -> int:
    return int(r, 16)


def parse_value(v: str) -> int:
    v = v.strip()
    if len(v) > 2:
        match v[:2]:
            case "0x":
                base, v = 16, v[2:]
            case "0o":
                base, v = 8, v[2:]
            case "0b":
                base, v = 2, v[2:]
            case _:
                base = 10
    else:
        base = 10
    return int(v, base)


def pieces(line: str, splitter: str) -> list[str]:
    """Splits by splitter if splitter not part of a string."""
    result = list[str]()
    split = True
    start = 0
    for i, c in enumerate(line):
        if c == '"':
            split = not split
            continue
        if split and c == splitter:
            result.append(line[start:i].strip())
            start = i + 1
    else:
        result.append(line[start : len(line)].strip())
    return result


@dataclass
class Assembled:
    raw_program: str
    pc: int
    words: list[int]
    address_mappings: dict[str, int]


def assemble(code: str, show_addresses=True) -> Assembled:
    machine_code = list[int]()
    pc = 0
    lines = list[str]()

    for line in [
        stripped
        for line in code.splitlines()
        if (stripped := pieces(line, ";")[0].strip())
    ]:
        if ":" in line:
            try:
                label, content = pieces(line, ":")
                lines.append(label.strip() + ":")
                if content.strip():
                    lines.append(content.strip())
            except ValueError:
                raise ToyException(f"Label error: {line}")
        else:
            lines.append(line)

    labels = dict[str, int]()
    addresses = dict[str, list[int]]()

    def write_to_special(addr: int, r=0) -> None:
        machine_code.append(0x9000 | addr | (r << 8))

    for line in lines:
        expression_found = False

        m = expressions["label"].match(line)
        if m:
            label = m.group(1)
            if label in labels:
                raise ToyException(f"Duplicate label: '{label}'.")
            labels[label] = len(machine_code)
            continue

        m = expressions[".data"].match(line)
        if m:
            machine_code.extend(
                [parse_value(v) & 0xFFFF for v in m.group(1).split(",")]
            )
            continue

        m = expressions[".ascii"].match(line)
        if m:

            def append_ascii(string: str) -> None:
                if string:
                    if len(string) > 2 and string[:2] == r"\0":
                        machine_code.append(0)
                        append_ascii(string[2:])
                    else:
                        first, rest = string[0], string[1:]
                        machine_code.append(ord(first) & 0xFF)
                        append_ascii(rest)

            append_ascii(m.group(1))
            machine_code.append(0)
            continue

        for special, addr in {
            ".char": 0xF5,
            ".bin": 0xF1,
            ".oct": 0xF2,
            ".den": 0xF4,
            ".hex": 0xF3,
            ".pattern": 0xF7,
        }.items():
            m = expressions[special].match(line)
            if m:
                d = parse_register(m.group(1))
                write_to_special(addr, d)
                expression_found = True
                break

        if expression_found:
            continue

        for special, addr in {
            ".input": 0xF0,
            ".rand": 0xFA,
            ".string": 0xFB,
        }.items():
            m = expressions[special].match(line)
            if m:
                d = parse_register(m.group(1))
                machine_code.append(
                    # R[d] <- input source
                    0x8000 | (d << 8) | addr
                )
                expression_found = True

        if expression_found:
            continue

        m = expressions[".main"].match(line)
        if m:
            pc = len(machine_code)
            continue

        m = expressions[".word"].match(line)
        if m:
            machine_code.append(0x0000)
            continue

        for special, addr in {
            ".dump": 0xF8,
            ".line": 0xF6,
            ".state": 0xF9,
        }.items():
            m = expressions[special].match(line)
            if m:
                write_to_special(addr)
                expression_found = True
                break

        if expression_found:
            continue

        m = expressions["halt"].match(line)
        if m:
            machine_code.append(0x0000)
            continue

        m = expressions["not d t"].match(line)
        if m:
            d = parse_register(m.group(1))
            s = parse_register(m.group(2))
            machine_code.extend(
                [
                    *store_word_to(
                        0xE,
                        0xFFFF,
                    ),
                    # R[d] <- R[s] ^ R[E]
                    0x400E | (d << 8) | (s << 4),
                ]
            )
            continue

        m = expressions["not d v"].match(line)
        if m:
            d = parse_register(m.group(1))
            v = parse_value(m.group(2))
            if v <= 0xFF:
                machine_code.append(
                    # R[D] <- v
                    0x7D00 | v,
                )
            else:
                machine_code.extend(
                    store_word_to(0xD, v),
                )

            machine_code.extend(
                [
                    *store_word_to(
                        0xE,
                        0xFFFF,
                    ),
                    # R[d] <- R[D] ^ R[E]
                    0x40DE | (d << 8),
                ]
            )
            continue

        m = expressions["load d l"].match(line)
        if m:
            d = parse_register(m.group(1))
            label = m.group(2)
            if label not in addresses:
                addresses[label] = []
            addresses[label].append(len(machine_code))
            machine_code.append(
                # R[d] <- ??
                0x7000 | (d << 8),
            )
            continue

        m = expressions["load d v"].match(line)
        if m:
            d = parse_register(m.group(1))
            addr = parse_value(m.group(2))

            if addr <= 0xFF:
                machine_code.append(
                    # R[d] <- v
                    0x7000 | (d << 8) | addr,
                )
                continue

            machine_code.extend(
                [
                    *store_word_to(0xE, addr),
                    # R[d] <- 0
                    0x7000 | (d << 8),
                    # R[d] <- R[d] + R[E]
                    0x100E | (d << 8) | (d << 4),
                ]
            )
            continue

        m = expressions["load d a"].match(line)
        if m:
            d = parse_register(m.group(1))
            addr = parse_value(m.group(2))
            machine_code.append(
                # R[d] <- addr
                0x8000 | (d << 8) | (addr & 0xFF),
            )
            continue

        m = expressions["store d la"].match(line)
        if m:
            addr = parse_value(m.group(1))
            s = parse_register(m.group(2))
            machine_code.append(
                # M[addr] <- R[s]
                0x9000 | (s << 8) | (addr & 0xFF),
            )
            continue

        m = expressions["load d la"].match(line)
        if m:
            d = parse_register(m.group(1))
            label = m.group(2)
            if label not in addresses:
                addresses[label] = []
            addresses[label].append(len(machine_code))
            machine_code.append(
                # R[d] <- M[??]
                0x8000 | (d << 8),
            )
            continue

        m = expressions["move d s"].match(line)
        if m:
            d, s = (parse_register(m.group(g)) for g in (1, 2))
            machine_code.extend(
                [
                    # R[d] <- 0
                    0x7000 | (d << 8),
                    # R[d] <- R[d] + R[s]
                    0x1000 | (d << 8) | (d << 4) | s,
                ]
            )
            continue

        m = expressions["load d p"].match(line)
        if m:
            d = parse_register(m.group(1))
            p = parse_register(m.group(2))
            machine_code.append(
                # R[d] <- M[R[p]]
                0xA000 | (d << 8) | p,
            )
            continue

        m = expressions["store p s"].match(line)
        if m:
            p = parse_register(m.group(1))
            s = parse_register(m.group(2))
            machine_code.append(
                # M[R[p]] <- s
                0xB000 | (s << 8) | p,
            )
            continue

        m = expressions["store la s"].match(line)
        if m:
            label = m.group(1)
            s = parse_register(m.group(2))
            if label not in addresses:
                addresses[label] = []
            addresses[label].append(len(machine_code))
            machine_code.append(
                # M[??] <- R[s]
                0x9000 | (s << 8),
            )
            continue

        m = expressions["jz d a"].match(line)
        if m:
            d = parse_register(m.group(1))
            addr = parse_value(m.group(2))
            machine_code.append(
                # if R[d] == 0 PC <- v
                0xC000 | (d << 8) | (addr & 0xFF),
            )
            continue

        m = expressions["jz d l"].match(line)
        if m:
            d = parse_register(m.group(1))
            label = m.group(2)
            if label not in addresses:
                addresses[label] = []
            addresses[label].append(len(machine_code))
            machine_code.append(
                # if R[d] == 0 PC <- ??
                0xC000 | (d << 8),
            )
            continue

        m = expressions["jp d a"].match(line)
        if m:
            d = parse_register(m.group(1))
            addr = parse_value(m.group(2))
            machine_code.append(
                # if R[d] > 0 PC <- v
                0xD000 | (d << 8) | (addr & 0xFF),
            )
            continue

        m = expressions["jp d l"].match(line)
        if m:
            d = parse_register(m.group(1))
            label = m.group(2)
            if label not in addresses:
                addresses[label] = []
            addresses[label].append(len(machine_code))
            machine_code.append(
                # if R[d] > 0 PC <- ??
                0xD000 | (d << 8),
            )
            continue

        m = expressions["jmp a"].match(line)
        if m:
            addr = parse_value(m.group(1))
            machine_code.extend(
                [
                    # R[F] <- v
                    0x7F00 | (addr & 0xFF),
                    # PC <- R[F]
                    0xEF00,
                ]
            )
            continue

        m = expressions["jmp l"].match(line)
        if m:
            label = m.group(1)
            if label not in addresses:
                addresses[label] = []
            addresses[label].append(len(machine_code))
            machine_code.extend(
                [
                    # R[F] <- ??
                    0x7F00,
                    # PC <- R[F]
                    0xEF00,
                ]
            )
            continue

        m = expressions["call d a"].match(line)
        if m:
            d = parse_register(m.group(1))
            addr = parse_value(m.group(2))
            machine_code.append(
                # R[d] <- PC; PC <- addr
                0xF000 | (d << 8) | (addr & 0xFF),
            )
            continue

        m = expressions["call d l"].match(line)
        if m:
            d = parse_register(m.group(1))
            label = m.group(2)
            if label not in addresses:
                addresses[label] = []
            addresses[label].append(len(machine_code))
            machine_code.append(
                # R[d] <- PC; PC <- ??
                0xF000 | (d << 8),
            )
            continue

        m = expressions["ret d"].match(line)
        if m:
            d = parse_register(m.group(1))
            machine_code.append(
                # PC <- R[d]
                0xE000 | (d << 8),
            )
            continue

        m = expressions["op d s t"].match(line)
        if m:
            op = m.group(1).lower()
            d, s, t = (parse_register(m.group(g)) for g in (2, 3, 4))
            if op == "or":
                machine_code.extend(
                    [
                        # R[E] <- R[s] & R[t]
                        0x3E00 | (s << 4) | t,
                        # R[F] <- R[s] ^ R[t]
                        0x4F00 | (s << 4) | t,
                        # R[d] <- R[E] ^ R[F]
                        0x40EF | (d << 8),
                    ]
                )
                continue
            if op in op_map:
                machine_code.append(
                    # R[d] <- R[s] * R[t]
                    (op_map[op] << 12) | (d << 8) | (s << 4) | t,
                )
                continue

            raise ToyException(f"Unknown operator: '{op}'.")

        m = expressions["op d s v"].match(line)
        if m:
            op = m.group(1).lower()
            d, s = (parse_register(m.group(g)) for g in (2, 3))
            v = parse_value(m.group(4))

            if v <= 0xFF:
                machine_code.append(
                    # R[E] <- v
                    0x7E00 | v,
                )
            else:
                machine_code.extend(
                    store_word_to(0xE, v),
                )

            if op == "or":
                machine_code.extend(
                    [
                        # R[F] <- R[E] ^ R[s]
                        0x4FE0 | s,
                        # R[E] <- R[E] & R[s]
                        0x3EE0 | s,
                        # R[d] <- R[E] ^ R[F]
                        0x40EF | (d << 8),
                    ]
                )
                continue

            if op in op_map:
                machine_code.append(
                    # R[d] <- R[s] * R[E]
                    0x000E | (op_map[op] << 12) | (d << 8) | (s << 4),
                )
                continue

            raise ToyException(f"Unknown operator: '{op}'.")

        m = expressions["op d s"].match(line)
        if m:
            op = m.group(1).lower()
            d, s = (parse_register(m.group(g)) for g in (2, 3))

            if op == "or":
                machine_code.extend(
                    [
                        # R[E] <- R[d] & R[s]
                        0x3E00 | (d << 4) | s,
                        # R[F] <- R[d] ^ R[s]
                        0x4F00 | (d << 4) | s,
                        # R[d] <- R[E] ^ R[F]
                        0x40EF | (d << 8),
                    ]
                )
                continue

            if op in op_map:
                machine_code.append(
                    # R[d] <- R[d] * R[s]
                    (op_map[op] << 12) | (d << 8) | (d << 4) | s,
                )
                continue

            raise ToyException(f"Unknown operator: '{op}'.")

        m = expressions["op d v"].match(line)
        if m:
            op = m.group(1).lower()
            d = parse_register(m.group(2))
            v = parse_value(m.group(3))

            if v <= 0xFF:
                machine_code.append(
                    # R[E] <- v
                    0x7E00 | v,
                )
            else:
                machine_code.extend(
                    store_word_to(0xE, v),
                )

            if op == "or":
                machine_code.extend(
                    [
                        # R[F] <- R[E] ^ R[d]
                        0x4FE0 | d,
                        # R[E] <- R[E] & R[d]
                        0x3EE0 | d,
                        # R[d] <- R[E] ^ R[F]
                        0x40EF | (d << 8),
                    ]
                )
                continue

            if op in op_map:
                machine_code.append(
                    # R[d] <- R[d] * R[E]
                    0x000E | (op_map[op] << 12) | (d << 8) | (d << 4),
                )
                continue

            raise ToyException(f"Unknown operator: '{op}'.")

        raise ToyException(f"Cannot parse line: '{line}'")

    for label, indices in addresses.items():
        if label in labels:
            address = labels[label]
            for index in indices:
                machine_code[index] |= address
        else:
            raise ToyException(f"Unrecognized label: '{label}'")

    if show_addresses:
        print("\nAddress Mappings:\n")
        for label, v in labels.items():
            print(f"  {label}: {hex(v)[2:].rjust(2, "0")}")
        print()
    return Assembled(code, pc, machine_code, labels)


def format_assembly(code: str) -> str:
    try:
        assembled = assemble(code, False)
        label_width = max(len(label) for label in assembled.address_mappings) + 1
        lines = code.splitlines()
        html = '<pre class="toy-assembly">\n'

        def format_argument(argument: str) -> str:
            m = match(pat("register"), argument)
            if m:
                return f'<span class="register">{argument}</span>'
            m = match(pat("at_register"), argument)
            if m:
                return f'[<span class="register">%{m.group(1)}</span>]'
            m = match(pat("label"), argument)
            if m:
                return f'<span class="label">{argument}</span>'
            m = match(pat("at_label"), argument)
            if m:
                return f'[<span class="label">{m.group(1)}</span>]'
            m = match(pat("value"), argument)
            if m:
                return f'<span class="literal">{argument}</span>'
            m = match(pat("at_address"), argument)
            if m:
                return f'[<span class="literal">{m.group(1)}</span>]'
            return f"<h1>Huh? {argument}</h1>"

        for line in lines:
            label, comment, instruction, argument = "", "", "", ""
            ps = pieces(line, ";")
            if len(ps) >= 2:
                line, comment = ps[0].strip(), ("; " + "".join(ps[1:])).strip()

            if line:
                ps = pieces(line, ":")
                if len(ps) >= 2:
                    label, line = ps[0].strip() + ":", "".join(ps[1:]).strip()
                if line:
                    ps = [
                        stripped for p in pieces(line, " ") if (stripped := p.strip())
                    ]
                    if ps:
                        instruction = (
                            f'<span class="special">{ps[0]}</span>'
                            if "." in ps[0]
                            else f'<span class="keyword">{ps[0]}</span>'
                        )
                        match ps[0]:
                            case ".ascii":
                                argument = (
                                    f'<span class="string">{" ".join(ps[1:])}</span>'
                                )
                            case ".data":
                                # In case no spaces between commas...
                                argument_pieces = list[str]()
                                for p in ps[1:]:
                                    argument_pieces.extend(n for n in p.split(",") if n)
                                argument = ", ".join(
                                    format_argument(p) for p in argument_pieces
                                )
                            case _:
                                argument = " ".join(format_argument(p) for p in ps[1:])

            html += (
                f'<span class="label">{label.rjust(label_width)}</span>'
                if label
                else " " * label_width
            )

            if instruction or argument:
                html += f" {instruction} {argument}"
            if comment:
                html += f'<span class="comment"> {comment}</span>'

            html += "\n"

        html += "</pre>"
        return r"""
<!doctype html>

<html lang="en">

<head>
  <meta charset="utf-8">
  <title>Assembly</title>
  <style>
    .toy-assembly {
      font-family: 'IBM Plex Mono', monospace;
      padding: 0.5em;
      border-top: 1pt solid;
      border-bottom: 1pt solid;
      line-height: 1.4em;
    }

    .label {
      font-style: italic;
    }

    .string {
      color: brown;
    }

    .keyword {
      font-weight: 500;
      color: cornflowerblue;
    }

    .special {
      color: blueviolet;
    }

    .literal {
      color: slateblue;
    }

    .comment {
      color: coral;
    }

    .register {
      color: forestgreen;
    }
  </style>

</head>

<body>

  <<code>>

</body>

</html>
""".replace("<<code>>", html)
    except ToyException as e:
        return f"Invalid assembly.\n{e.message}"
