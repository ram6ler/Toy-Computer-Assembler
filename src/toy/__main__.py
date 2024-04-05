from .toy_computer import ToyComputer
from .assembler import assemble

if __name__ == "__main__":
    from re import split
    from sys import argv
    from .exception import ToyException

    def repl():
        print(
            r"""
.-----------------.
|         _____   |
|        |_   _|__ _  _
|          | |/ _ \ || |
|    ___   |_|\___/\_, |     _
|   / __|___  ___  |__/ _  _| |_ ___ _ _
'--| (__/ _ \/ ' \| '_ \ || |  _/ -_) '_|
    \___\___/_|_|_| .__/\_,_|\__\___|_|
                  |_|       Version 0.0.1

Input 'help' to get started.
          """
        )

        loaded_program = ""
        loaded_type = ""
        computer = ToyComputer()

        def reset() -> bool:
            match loaded_type:
                case "asm":
                    pc, ram = assemble(loaded_program)
                    computer.set_state(pc, ram)
                    return True
                case "ml":
                    computer.compile_machine_language(loaded_program)
                    return True
                case _:
                    print("No program loaded...")
                    return False

        while True:
            instructions = split(r" +", input("\n> "))

            match instructions:
                case ["help"] | ["h"]:
                    print(
                        """
    To use:

      help              Displays this help message.

      about             Further information about Toy
                        Computer.
                                              
      compile [file]    Compiles and loads Toy Machine or
                        Toy Assembly language file. (If
                        .asm is contained in the file name
                        the language is assumed to be Toy
                        Assembly.)

      run               Runs the program
                          
      

    """
                    )
                    continue
                case ["about"] | ["a"]:
                    print(
                        """
    Toy Computer is a Python implementation of an imaginary
    computer described in chapter 6 of:

      Sedgewick, R. & Wayne, K. (2017)
      Computer Science: An Interdisciplinary Approach.

    This implementation (and Toy Assembly) was created by
    Richard Ambler for use in computer science courses at
    Beijing World Youth Academy.

    For further details, see:

        https://github.com/ram6ler/Toy-Computer-Assembler
    """
                    )
                case ["compile", file] | ["c", file]:
                    try:
                        with open(file) as f:
                            program = f.read()
                    except FileNotFoundError:
                        print(f"File '{file}' not found...")
                        continue
                    try:
                        if ".asm" in file:
                            pc, ram = assemble(program)
                            computer.set_state(pc, ram)
                            loaded_program = program
                            loaded_type = "asm"
                            print(f"Done. Compiled {file} as assembly.")
                        else:
                            computer.compile_machine_language(program)
                            loaded_program = program
                            loaded_type = "ml"
                            print(f"Done. Compiled {file} as machine language.")

                    except ToyException as e:
                        print("* Error:")
                        print(e.message)

                case ["run"] | ["r"]:
                    reset()
                    print(" Run Started".rjust(80, "."))
                    computer.run()
                    print()
                    print(" Run Ended".rjust(80, "."))
                case ["reset"] | ["."]:
                    reset()
                    print("Done.")
                case ["step", *rest] | ["s", *rest]:
                    s_pc = hex(computer.pc)[2:].rjust(2, "0")
                    s_cir = hex(computer.memory[computer.pc])[2:].rjust(4, "0")
                    pseudo = ToyComputer.as_pseudocode(computer.memory[computer.pc])
                    print(f"PC: 0x{s_pc} CIR: 0x{s_cir} Pseudocode: {pseudo}")
                    print(" Step Started".rjust(80, "."))
                    more_steps = computer.step()
                    if not more_steps:
                        print("(Program complete.)")
                    print()
                    print(" Step Ended".rjust(80, "."))

                    if "dump" in rest or "d" in rest:
                        print(computer.dump())
                    if "ml" in rest or "m" in rest:
                        print(computer.state_to_machine_language())
                case ["dump"] | ["d"]:
                    print(computer.dump())
                case ["ml"] | ["m"]:
                    print(computer.state_to_machine_language())
                case ["quit"] | ["q"]:
                    print("So long!")
                    exit()
                case _:
                    print("Not understood. Type in help for available instructions.")

    if len(argv) == 1:
        repl()
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
