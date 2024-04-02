from random import randrange
from .exception import ToyException


def _readInteger() -> int:
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
            return int(result, base)
        except ValueError:
            print("* Invalid input. Try again: ", end="")


def _nibble(x: int) -> str:
    return hex(x)[2:]


def _byte(x: int) -> str:
    return hex(x)[2:].rjust(2, "0")


class ToyComputer:
    def __init__(self) -> None:
        self.registers = [0 for _ in range(0x10)]
        self.memory = [0 for _ in range(0x100)]
        self.pc = 0

    @staticmethod
    def decode(instruction: int) -> tuple[int, int, int, int, int]:
        return (
            (instruction & 0xF000) >> 12,
            (instruction & 0x0F00) >> 8,
            (instruction & 0x00F0) >> 4,
            instruction & 0x000F,
            instruction & 0x00FF,
        )

    @staticmethod
    def pseudo(instruction: int) -> str:
        op, d, s, t, addr = ToyComputer.decode(instruction)
        match op:
            case 0x0:
                return "-"
            case 0x1:
                return f"R[{_nibble(d)}] <- R[{_nibble(s)}] + R[{_nibble(t)}]"
            case 0x2:
                return f"R[{_nibble(d)}] <- R[{_nibble(s)}] - R[{_nibble(t)}]"
            case 0x3:
                return f"R[{_nibble(d)}] <- R[{_nibble(s)}] & R[{_nibble(t)}]"
            case 0x4:
                return f"R[{_nibble(d)}] <- R[{_nibble(s)}] ^ R[{_nibble(t)}]"
            case 0x5:
                return f"R[{_nibble(d)}] <- R[{_nibble(s)}] << R[{_nibble(t)}]"
            case 0x6:
                return f"R[{_nibble(d)}] <- R[{_nibble(s)}] >> R[{_nibble(t)}]"
            case 0x7:
                return f"R[{_nibble(d)}] <- {_nibble(addr)}"
            case 0x8:
                return f"R[{_nibble(d)}] <- M[{_byte(addr)}]"
            case 0x9:
                return f"M[{_byte(addr)}] <- R[{_nibble(d)}]"
            case 0xA:
                return f"R[{_nibble(d)}] <- M[R[{_nibble(t)}]]"
            case 0xB:
                return f"M[R[{_nibble(t)}]] <- R[{_nibble(d)}]"
            case 0xC:
                return f"if (R[{_nibble(d)}] == 0) PC <- {_byte(addr)}"
            case 0xD:
                return f"if (R[{_nibble(d)}] > 0) PC <- {_byte(addr)}"
            case 0xE:
                return f"PC <- R[{_nibble(d)}]"
            case 0xF:
                return f"R[{_nibble(d)}] <- PC; PC <- {_byte(addr)}"
            case _:
                return ""

    def step(self) -> bool:
        def store(addr: int, r_index: int) -> None:
            match addr:
                case 0xF1:
                    # binary out
                    print(bin(self.registers[r_index])[2:], end="")
                case 0xF2:
                    # octal out
                    print(oct(self.registers[r_index])[2:], end="")
                case 0xF3:
                    # hexadecimal out
                    print(hex(self.registers[r_index])[2:], end="")
                case 0xF4:
                    # denary out
                    print(self.registers[r_index], end="")
                case 0xF5:
                    # char out
                    print(chr(self.registers[r_index]), end="")
                case 0xF6:
                    # new line
                    print()
                case 0xF7:
                    # pattern
                    print(
                        bin(self.registers[r_index])[2:]
                        .replace("0", " ")
                        .replace("1", "█")
                        .rjust(16)
                    )
                case 0xF8:
                    # dump
                    print(f"\n{self.dump()}")
                case 0xF9:
                    # state
                    print(f"\n{self.state_to_machine_code()}")
                case _:
                    self.memory[addr] = self.registers[r_index]

        def load(addr: int, r_index: int) -> None:
            match addr:
                case 0xF0:
                    self.registers[r_index] = _readInteger()
                case 0xFA:
                    self.registers[r_index] = randrange(0x10000)
                case _:
                    self.registers[r_index] = self.memory[addr]

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

    def execute(self) -> None:
        while self.step():
            pass

    def load(self, pc: int, ram: list[int], registers: list[int] = []) -> None:
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
            self.registers[i] = 0

    def load_machine_code(self, code: str) -> None:
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

        self.load(pc, ram, registers)

    def state_to_machine_code(self) -> str:
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
                    + column(ToyComputer.pseudo(v), 25)
                    + "\n"
                )
        return result

    def dump(self) -> str:
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
        result += f"{pad("IR:")}{pad(hex(ir)[2:].rjust(4, "0"))} {ToyComputer.pseudo(self.memory[self.pc])}"
        result += "\n\n"

        return result
