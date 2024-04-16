from .toy_computer import ToyComputer
from .assembler import assemble

if __name__ == "__main__":
    from re import split
    from sys import argv
    from .exception import ToyException

    def banner():
        print(
            r"""
       _____
      |_   _|__ _  _
        | |/ _ \ || |
        |_|\___/\_, |
     ___        |__/         _
    / __|___ _ __  _ __ _  _| |_ ___ _ _
   | (__/ _ \ '  \| '_ \ || |  _/ -_) '_|
    \___\___/_|_|_| .__/\_,_|\__\___|_|
                  |_|         Pre-alpha"""
        )

    def lineate(message: str) -> None:
        print(f" {message}".rjust(80, "."))

    def repl():
        banner()
        print()
        loaded_path = ""
        # loaded_program = ""
        # loaded_type = ""
        previous_step = ""
        repeat_previous_step = False
        original_pc = 0

        computer = ToyComputer()

        def load_path(path: str) -> bool:
            nonlocal loaded_path, original_pc
            try:
                with open(path) as f:
                    program = f.read()
            except FileNotFoundError:
                print(f"File '{path}' not found...")
                return False

            try:
                if ".asm" in path:
                    pc, ram = assemble(program)
                    computer.set_state(pc, ram)
                    print(f"Compiled {path} as assembly.")
                else:
                    computer.compile_machine_language(program)
                    print(f"Compiled {path} as machine language.")

                original_pc = computer.pc
                loaded_path = path
                return True
            except ToyException as e:
                print("* Error:")
                print(e.message)
                return False

        while True:
            if repeat_previous_step:
                repeat_previous_step = False
                instruction = previous_step
            else:
                instruction = input(f"\n{loaded_path.split("/")[-1]} > ")
            match split(r" +", instruction):
                case ["help"] | ["h"]:
                    print(
                        """
      To use:

        help (h)            Display this help message.

        about (a)           Display more information about Toy Computer.

        load (l) [p]        Compile and load a machine language or
                            assembly language file p. (If .asm is
                            contained in the file name the language
                            is assumed to be assembly.) If no path is
                            provided, re-compile loaded file.

        code (c)            Output the loaded assembly or machine language.

        reset (p)           Reset the program counter to its original position.

        run (r)             Run the program from the current position.

        dump (d) [p]        Output the memory and register data. If a path is
                            added, save dump to path p.

        machine (m)         Output the current state as machine language. (If
                            a path is added, save machine language to file.)

        step (s)            Step through one fetch-decode-execute cycle. (If
                            dump (d) or machine (m) are added, the step is
                            followed by the respective output.)

        repeat (.)          Repeat previous step instruction.

        [a] [i]             Write two-byte value i to one-byte memory address a.
                            Both a and i are expected to be in hexadecimal.

        clear (x)           Clear computer memory.

        quit (q)            Quit.
      """
                    )
                    continue
                case ["about"] | ["a"]:
                    banner()
                    print(
                        """
  Welcome to Toy Computer, a Python implementation of
  an imaginary computer described in chapter 6 of:

    Sedgewick, R. & Wayne, K. (2017)
    Computer Science: An Interdisciplinary Approach

  This implementation (and Toy Assembly) was created by
  Richard Ambler for use in computer science courses at
  Beijing World Youth Academy.

  For further details, see:

    https://github.com/ram6ler/Toy-Computer-Assembler
"""
                    )
                case ["load", path] | ["l", path]:
                    load_path(path)

                case ["load"] | ["l"]:
                    if loaded_path:
                        load_path(loaded_path)
                    else:
                        print("No program loaded...")

                case ["code"] | ["c"]:
                    if loaded_path:
                        try:
                            print()
                            with open(loaded_path) as f:
                                print(f.read())
                        except FileNotFoundError:
                            print(f"Cannot find '{loaded_path}'...")
                    else:
                        print("No file loaded...")

                case ["run"] | ["r"]:
                    if computer.ir:
                        lineate("Run Started")
                        try:
                            computer.run()
                            print()
                            lineate("Run Ended")
                        except KeyboardInterrupt:
                            print()
                            lineate("* Interrupted")

                    else:
                        print("Program completed.")

                case ["reset"] | ["p"]:
                    computer.pc = original_pc
                    print(
                        f"Program counter reset to {hex(original_pc)[2:].rjust(2, "0")}."
                    )

                case ["clear"] | ["x"]:
                    loaded_path = ""
                    previous_step = ""
                    repeat_previous_step = False
                    original_pc = 0
                    computer.clear()
                    print("Cleared.")

                case ["step", *rest] | ["s", *rest]:
                    s_pc = hex(computer.pc)[2:].rjust(2, "0")
                    s_cir = hex(computer.memory[computer.pc])[2:].rjust(4, "0")
                    pseudo = ToyComputer.as_pseudocode(computer.memory[computer.pc])
                    print(f"PC: 0x{s_pc} CIR: 0x{s_cir} Pseudocode: {pseudo}")
                    lineate("Step Started")
                    try:
                        more_steps = computer.step()
                        if not more_steps:
                            print("(Program complete.)")
                            print()
                            lineate("Step Ended")
                            if "dump" in rest or "d" in rest:
                                print(computer.dump())
                            if "machine" in rest or "m" in rest:
                                print(computer.state_to_machine_language())
                            previous_step = instruction
                    except ToyException as e:
                        print("* Error")
                        print(e.message)

                case ["repeat"] | ["."]:
                    if previous_step:
                        repeat_previous_step = True
                    else:
                        print("No step instructions input yet...")

                case ["dump", *rest] | ["d", *rest]:
                    if rest:
                        with open(rest[0], "w") as f:
                            f.write(computer.dump())
                        print(f"Dump written to {rest[0]}.")
                    else:
                        print(computer.dump())

                case ["machine", *rest] | ["m", *rest]:
                    if rest:
                        with open(rest[0], "w") as f:
                            f.write(computer.state_to_machine_language())
                        print(f"State as machine language written to {rest[0]}.")
                    else:
                        print(computer.state_to_machine_language())

                case ["quit"] | ["q"]:
                    print("\n\nSo long!\n")
                    exit()

                case [sa, sv]:
                    if sa.lower() == "pc":
                        try:
                            a = int(sv, 16)
                            if a < 0 or a > 0xFF:
                                print("Expecting a one-byte value...")
                            else:
                                computer.pc = a
                                print(f"PC <- {hex(a)[2:].rjust(2, "0")}")
                        except ValueError:
                            print(
                                "Not understood. "
                                "Input 'help' for available instructions."
                            )
                    else:
                        try:
                            a = int(sa, 16)
                        except ValueError:
                            print(
                                "Not understood. "
                                "Input 'help' for available instructions."
                            )
                            continue
                        if a < 0 or a > 0xFF:
                            print("Addresses range from 00 to FF...")
                            continue
                        try:
                            v = int(sv, 16)
                        except ValueError:
                            print(
                                "Not understood. "
                                "Input 'help' for available instructions."
                            )
                            continue
                        if v < 0 or v > 0xFFFF:
                            print(f"Value {hex(v)} cannot be stored in two bytes...")
                            continue
                        print(
                            f"M[{hex(a)[2:].rjust(2, "0")}] "
                            f"{hex(computer.memory[a])[2:].rjust(4, "0")} -> "
                            f"{hex(v)[2:].rjust(4, "0")}\n{ToyComputer.as_pseudocode(v)}"
                        )
                        computer.memory[a] = v

                case _:
                    print("Not understood. Input 'help' for available instructions.")

    if len(argv) == 1:
        try:
            repl()
        except KeyboardInterrupt:
            print("\n\nSo long!\n")
    elif len(argv) == 2:
        try:
            with open(argv[1]) as f:
                code = f.read()
        except FileNotFoundError:
            print(f"File '{argv[1]}' not found...")
            exit()

        computer = ToyComputer()
        if ".asm" in argv[1]:
            pc, ram = assemble(code)
            computer.set_state(pc, ram)
        else:
            computer.compile_machine_language(code)
        computer.run()
    else:
        print(
            """
  To use:
    python -m toy
  or:
    python -m toy [file]
  """
        )
