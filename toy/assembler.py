from re import compile

from .exception import ToyException


def pat(s: str) -> str:
    match s:
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


expressions = {
    # Assembly
    "label": compile(f"^{pat("label")}: *$"),
    "halt": compile(r"^halt$"),
    "not d t": compile(f"^not{pat("register") * 2}$"),
    "and d s t": compile(f"^and{pat("register") * 3}$"),
    "and d s v": compile(f"^and{pat("register") * 2}{pat("value")}$"),
    "xor d s t": compile(f"^xor{pat("register") * 3}$"),
    "xor d s v": compile(f"^xor{pat("register") * 2}{pat("value")}$"),
    "lsh d s t": compile(f"^lsh{pat("register") * 3}$"),
    "lsh d s v": compile(f"^lsh{pat("register") * 2}{pat("value")}$"),
    "rsh d s t": compile(f"^rsh{pat("register") * 3}$"),
    "rsh d s v": compile(f"^rsh{pat("register") * 2}{pat("value")}$"),
    "add d s t": compile(f"^add{pat("register") * 3}$"),
    "add d s v": compile(f"^add{pat("register") * 2}{pat("value")}$"),
    "sub d s t": compile(f"^sub{pat("register") * 3}$"),
    "sub d s v": compile(f"^sub{pat("register") * 2}{pat("value")}$"),
    "or d s t": compile(f"^or{pat("register") * 3}$"),
    "or d s v": compile(f"^or{pat("register") * 2}{pat("value")}$"),
    "mov d v": compile(f"^mov{pat("register")}{pat("value")}$"),
    "mov d l": compile(f"^mov{pat("register")}{pat("label")}$"),
    "mov d a": compile(f"^mov{pat("register")}{pat("at_address")}$"),
    "mov a s": compile(f"^mov{pat("at_address")}{pat("register")}$"),
    "mov la d": compile(f"^mov{pat("at_label")}{pat("register")}$"),
    "mov d la": compile(f"^mov{pat("register")}{pat("at_label")}$"),
    "mov d s": compile(f"^mov{pat("register") * 2}$"),
    "mov d p": compile(f"^mov{pat("register")}{pat("at_register")}$"),
    "mov p s": compile(f"^mov{pat("at_register")}{pat("register")}$"),
    "jz d a": compile(f"^jz{pat("register")}{pat("value")}$"),
    "jz d l": compile(f"^jz{pat("register")}{pat("label")}$"),
    "jp d a": compile(f"^jp{pat("register")}{pat("value")}$"),
    "jp d l": compile(f"^jp{pat("register")}{pat("label")}$"),
    "jump a": compile(f"^jump{pat("value")}$"),
    "jump l": compile(f"^jump{pat("label")}$"),
    "proc d a": compile(f"^proc{pat("register")}{pat("value")}$"),
    "proc d l": compile(f"^proc{pat("register")}{pat("label")}$"),
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


def assemble(code: str) -> tuple[int, list[int]]:
    machine_code = list[int]()
    pc = 0
    lines = [
        stripped
        for line in code.split("\n")
        if (stripped := line.split(";;")[0].strip())
    ]
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
            machine_code.extend(
                [
                    *[ord(c) & 0xFFFF for c in m.group(1)],
                    0,
                ]
            )
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
                    0x400 | (d << 8) | (s << 4),
                ]
            )
            continue

        for op, op_code in {
            "and": 0x3,
            "xor": 0x4,
            "lsh": 0x5,
            "rsh": 0x6,
            "add": 0x1,
            "sub": 0x2,
        }.items():
            m = expressions[f"{op} d s t"].match(line)
            if m:
                d, s, t = (parse_register(m.group(g)) for g in (1, 2, 3))
                machine_code.append(
                    # R[d] <- R[s] * R[t]
                    t | (s << 4) | (d << 8) | (op_code << 12),
                )
                expression_found = True
                break
            m = expressions[f"{op} d s v"].match(line)
            if m:
                d, s = (parse_register(m.group(g)) for g in (1, 2))
                v = parse_value(m.group(3))
                if v <= 0xFF:
                    machine_code.append(
                        # R[F] <- v
                        0x7F00 | v,
                    )
                else:
                    machine_code.extend(
                        store_word_to(0xE, v),
                    )

                machine_code.append(
                    # R[d] <- R[s] * R[F]
                    0x000F | (op_code << 12) | (d << 8) | (s << 4),
                )
                expression_found = True
                break

        if expression_found:
            continue

        m = expressions["or d s t"].match(line)
        if m:
            d, s, t = (parse_register(m.group(g)) for g in (1, 2, 3))
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

        m = expressions["or d s v"].match(line)
        if m:
            d, s = (parse_register(m.group(g)) for g in (1, 2))
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

        m = expressions["mov d l"].match(line)
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

        m = expressions["mov d v"].match(line)
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

        m = expressions["mov d a"].match(line)
        if m:
            d = parse_register(m.group(1))
            addr = parse_value(m.group(2))
            machine_code.append(
                # R[d] <- addr
                0x8000 | (d << 8) | (addr & 0xFF),
            )
            continue

        m = expressions["mov a s"].match(line)
        if m:
            addr = parse_value(m.group(1))
            s = parse_register(m.group(2))
            machine_code.append(
                # M[addr] <- R[s]
                0x9000 | (s << 8) | (addr & 0xFF),
            )
            continue

        m = expressions["mov la d"].match(line)
        if m:
            label = m.group(1)
            d = parse_register(m.group(2))
            if label not in addresses:
                addresses[label] = []
            addresses[label].append(len(machine_code))
            machine_code.extend(
                [
                    # R[F] <- M[??]
                    0xAF00,
                    # M[R[F]] <- R[d]
                    0xB00F | (d << 8),
                ]
            )
            continue

        m = expressions["mov d la"].match(line)
        if m:
            d = parse_register(m.group(1))
            label = m.group(2)
            if label not in addresses:
                addresses[label] = []
            addresses[label].append(len(machine_code))
            machine_code.append(
                # R[d] <- M[??]
                0xA000 | (d << 8),
            )
            continue

        m = expressions["mov d s"].match(line)
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

        m = expressions["mov d p"].match(line)
        if m:
            d = parse_register(m.group(1))
            p = parse_register(m.group(2))
            machine_code.append(
                # R[d] <- M[R[p]]
                0xA000 | (d << 8) | p,
            )
            continue

        m = expressions["mov p s"].match(line)
        if m:
            p = parse_register(m.group(1))
            s = parse_register(m.group(2))
            machine_code.append(
                # M[R[p]] <- s
                0xB000 | (s << 8) | p,
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

        m = expressions["jump a"].match(line)
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

        m = expressions["jump l"].match(line)
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

        m = expressions["proc d a"].match(line)
        if m:
            d = parse_register(m.group(1))
            addr = parse_value(m.group(2))
            machine_code.append(
                # R[d] <- PC; PC <- addr
                0xF000 | (d << 8) | (addr & 0xFF),
            )
            continue

        m = expressions["proc d l"].match(line)
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

        raise ToyException(f"Cannot parse line: '{line}'")

    for label, indices in addresses.items():
        if label in labels:
            address = labels[label]
            for index in indices:
                machine_code[index] |= address
        else:
            raise ToyException(f"Unrecognized label: '{label}'")

    return pc, machine_code
