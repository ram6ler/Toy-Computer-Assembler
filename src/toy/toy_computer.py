from random import randrange
from .exception import ToyException


def readInteger() -> int:
    while True:
        result = input()
        if len(result) > 2:
            match result[:2]:
                case "0x":
                    base, result = 16, result[2:]
                case "0o":
                    base, result = 8, result[2:]
                case "0b":
                    base, result = 2, result[2:]
                case _:
                    base, result = 10, result
        else:
            base, result = 10, result

        try:
            v = int(result, base)
            w = abs(v) & 0xFFFF
            if v != w:
                print(f"* Taking input to be {hex(w)}")
            return w

        except ValueError:
            print("* Invalid input. Try again: ", end="")


def make_nibble(x: int) -> str:
    return hex(x)[2:]


def make_byte(x: int) -> str:
    return hex(x)[2:].rjust(2, "0")


class ToyComputer:
    def __init__(self) -> None:
        self.registers = [0 for _ in range(0x10)]
        self.memory = [0 for _ in range(0x100)]
        self.pc = 0

    @staticmethod
    def decode(instruction: int) -> tuple[int, int, int, int, int]:
        """
        Splits instruction into parts `op`, `d`, `s`, `t`, `addr`.
        """
        return (
            (instruction & 0xF000) >> 12,
            (instruction & 0x0F00) >> 8,
            (instruction & 0x00F0) >> 4,
            instruction & 0x000F,
            instruction & 0x00FF,
        )

    @staticmethod
    def as_pseudocode(instruction: int) -> str:
        """
        Returns a pseudocode description of an instruction value.
        """
        op, d, s, t, addr = ToyComputer.decode(instruction)
        match op:
            case 0x0:
                return "-"
            case 0x1:
                return (
                    f"R[{make_nibble(d)}] <- R[{make_nibble(s)}] + R[{make_nibble(t)}]"
                )
            case 0x2:
                return (
                    f"R[{make_nibble(d)}] <- R[{make_nibble(s)}] - R[{make_nibble(t)}]"
                )
            case 0x3:
                return (
                    f"R[{make_nibble(d)}] <- R[{make_nibble(s)}] & R[{make_nibble(t)}]"
                )
            case 0x4:
                return (
                    f"R[{make_nibble(d)}] <- R[{make_nibble(s)}] ^ R[{make_nibble(t)}]"
                )
            case 0x5:
                return (
                    f"R[{make_nibble(d)}] <- R[{make_nibble(s)}] << R[{make_nibble(t)}]"
                )
            case 0x6:
                return (
                    f"R[{make_nibble(d)}] <- R[{make_nibble(s)}] >> R[{make_nibble(t)}]"
                )
            case 0x7:
                return f"R[{make_nibble(d)}] <- {make_nibble(addr)}"
            case 0x8:
                return f"R[{make_nibble(d)}] <- M[{make_byte(addr)}]"
            case 0x9:
                return f"M[{make_byte(addr)}] <- R[{make_nibble(d)}]"
            case 0xA:
                return f"R[{make_nibble(d)}] <- M[R[{make_nibble(t)}]]"
            case 0xB:
                return f"M[R[{make_nibble(t)}]] <- R[{make_nibble(d)}]"
            case 0xC:
                return f"if (R[{make_nibble(d)}] == 0) PC <- {make_byte(addr)}"
            case 0xD:
                return f"if (R[{make_nibble(d)}] > 0) PC <- {make_byte(addr)}"
            case 0xE:
                return f"PC <- R[{make_nibble(d)}]"
            case 0xF:
                return f"R[{make_nibble(d)}] <- PC; PC <- {make_byte(addr)}"
            case _:
                return ""

    def step(self) -> bool:
        """
        Performs a single fetch-decode-execute cycle.
        """

        def store(memory_address: int, register_address: int) -> None:
            """
            Stores value into memory or performs special output operation.
            """
            match memory_address:
                case 0xF1:
                    # binary out
                    print(bin(self.registers[register_address])[2:], end="")
                case 0xF2:
                    # octal out
                    print(oct(self.registers[register_address])[2:], end="")
                case 0xF3:
                    # hexadecimal out
                    print(hex(self.registers[register_address])[2:], end="")
                case 0xF4:
                    # denary out
                    print(self.registers[register_address], end="")
                case 0xF5:
                    # char out
                    print(chr(self.registers[register_address]), end="")
                case 0xF6:
                    # new line
                    print()
                case 0xF7:
                    # pattern
                    print(
                        bin(self.registers[register_address])[2:]
                        .replace("0", " ")
                        .replace("1", "█")
                        .rjust(16)
                    )
                case 0xF8:
                    # dump
                    print(f"\n{self.dump()}")
                case 0xF9:
                    # state
                    print(f"\n{self.state_to_machine_language()}")
                case _:
                    self.memory[memory_address] = self.registers[register_address]

        def load(memory_address: int, register_address: int) -> None:
            """
            Loads value into register or performs special input operation.
            """
            match memory_address:
                case 0xF0:
                    # Load an integer value.
                    self.registers[register_address] = readInteger()
                case 0xFA:
                    # Load a random word.
                    self.registers[register_address] = randrange(0x10000)
                case 0xFB:
                    # Store a string starting at address in register.
                    data = [x for c in input() if (x := ord(c)) >= 0x20 and x <= 0x7F]
                    start = self.registers[register_address]
                    for i, v in enumerate(data):
                        if (address := start + i) < len(self.memory):
                            self.memory[address] = v
                        else:
                            break
                case _:
                    # R[d] <- M[addr]
                    self.registers[register_address] = self.memory[memory_address]

        ir = self.memory[self.pc]
        op, d, s, t, addr = ToyComputer.decode(ir)
        self.pc += 1

        match op:
            case 0x0:
                # Halt
                self.pc -= 1
            case 0x1:
                # R[D] <- R[S] + R[T]
                self.registers[d] = self.registers[s] + self.registers[t]
            case 0x2:
                # R[D] <- R[S] - R[T]
                self.registers[d] = self.registers[s] - self.registers[t]
            case 0x3:
                # R[D] <- R[S] & R[T]
                self.registers[d] = self.registers[s] & self.registers[t]
            case 0x4:
                # R[D] <- R[S] ^ R[T]
                self.registers[d] = (self.registers[s] & 0xFFFF) ^ (
                    self.registers[t] & 0xFFFF
                )
            case 0x5:
                # R[D] <- R[S] << R[T]
                self.registers[d] = self.registers[s] << self.registers[t]
            case 0x6:
                # R[D] <- R[S] >> R[T]
                self.registers[d] = self.registers[s] >> self.registers[t]
            case 0x7:
                # R[D] <- addr
                self.registers[d] = addr
            case 0x8:
                # R[D] <- mem[addr]
                load(addr, d)
            case 0x9:
                # mem[addr] <- R[D]
                store(addr, d)
            case 0xA:
                # R[D] <- mem[R[T]]
                load(self.registers[t] & 0x00FF, d)
            case 0xB:
                # mem[R[T]] < R[D]
                store(self.registers[t] & 0x00FF, d)
            case 0xC:
                # R[D] == 0 ? PC <- addr
                if self.registers[d] == 0:
                    self.pc = addr
            case 0xD:
                # R[D] > 0 ? PC <- addr
                if self.registers[d] > 0:
                    self.pc = addr
            case 0xE:
                # PC <- R[d]
                self.pc = self.registers[d]
            case 0xF:
                # R[D] <- PC; PC <- addr
                self.registers[d] = self.pc
                self.pc = addr

        return (self.memory[self.pc] & 0xF000) != 0

    def run(self) -> None:
        """
        Repeats load-decode-execute cycle until halt is encountered.
        """
        while self.step():
            pass

    def set_state(
        self,
        pc: int,
        ram: list[int],
        registers: list[int] = [],
    ) -> None:
        """
        Sets the program counter, memory contents and register contents.
        """
        if pc < 0 or pc > 0xFF:
            raise ToyException("Bad program counter.")
        if len(ram) > 0x100:
            raise ToyException("Not enough memory.")
        self.pc = pc
        for i in range(0x100):
            if i < len(ram):
                self.memory[i] = ram[i]
            else:
                self.memory[i] = 0
        for i in range(0x10):
            if i < len(registers):
                self.registers[i] = registers[i]
            else:
                self.registers[i] = 0

    def compile_machine_language(self, code: str) -> None:
        """
        Compiles and loads machine language.

        Each line is expected to be of the form address: value. The
        program counter can be set using PC: value. Comments starting
        with a semi-colon are ignored.
        """
        pc = 0
        registers = [0 for _ in range(0x10)]
        ram = [0 for _ in range(0x100)]
        lines = [
            result
            for line in code.split("\n")
            if (result := line.split(";")[0].lower().strip())
        ]
        for line in lines:
            addr, instruction = line.split(":")
            try:
                if addr == "pc":
                    pc = int(instruction, base=0x10)
                elif addr[0] == "r":
                    index = int(addr[1], 0x10)
                    registers[index] = int(instruction, base=0x10)
                else:
                    index = int(addr, 0x10)
                    ram[index] = int(instruction, 0x10)
            except ValueError:
                raise ToyException(f"Bad instruction: {line}")

        self.set_state(pc, ram, registers)

    def state_to_machine_language(self) -> str:
        """
        Returns a compilable machine language representation
        of the current state.
        """

        def column(x: str, width=18):
            return x.rjust(width)

        result = column(f"PC: {hex(self.pc)[2:].rjust(2, "0")}") + "\n"
        for i, v in enumerate(self.registers):
            if v:
                result += column(f"R{hex(i)[2:]}: {hex(v)[2:].rjust(4, "0")}\n")
        result += f"{column(";;")}{column("Character")}{column("Decimal")}{column("Binary")}{column("Instruction", 25)}\n"
        for i, v in enumerate(self.memory):
            if v:
                result += (
                    column(f"{hex(i)[2:].rjust(2, "0")}: {hex(v)[2:].rjust(4, "0")};")
                    + column(f"'{chr(v)}'" if 0x20 <= v <= 0x7F else "-")
                    + column(str(v))
                    + column(bin(v)[2:].rjust(16, "0"))
                    + column(ToyComputer.as_pseudocode(v), 25)
                    + (" <-----" if self.pc == i else "")
                    + "\n"
                )
        return result

    def dump(self) -> str:
        """
        Returns a dump of all data in the current state.
        """

        def pad(x: str) -> str:
            return x.rjust(5)

        result = f"\n{pad("R")}"
        result += pad("") + pad("|") + pad("RAM")
        for i in range(0x10):
            result += pad("_" + hex(i)[2:])
        result += "\n"
        for r in range(0x10):
            result += pad(hex(r)[2:])
            result += pad(hex(self.registers[r])[2:].rjust(4, "0"))
            result += pad("|") + pad(hex(r)[2:] + "_")
            for c in range(0x10):
                index = r * 0x10 + c
                result += pad(hex(self.memory[index])[2:].rjust(4, "0"))
            result += "\n"
        result += f"\n{pad("PC:")}{pad(hex(self.pc)[2:].rjust(2, "0"))}"
        ir = self.memory[self.pc]
        result += f"{pad("IR:")}{pad(hex(ir)[2:].rjust(4, "0"))} {ToyComputer.as_pseudocode(self.memory[self.pc])}"
        result += "\n\n"

        return result
