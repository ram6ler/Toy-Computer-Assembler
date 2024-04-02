from .toy_computer import ToyComputer
from .assembler import assemble


if __name__ == "__main__":
    from sys import argv

    if len(argv) != 2:
        print("Expecting a file name.")
    else:
        computer = ToyComputer()
        try:
            with open(argv[1]) as f:
                code = f.read()
        except FileNotFoundError:
            print(f"File '{argv[1]}' not found...")
            exit()

        if ".asm" in argv[1]:
            pc, ram = assemble(code)
            computer.load(pc, ram)
        else:
            computer.load_machine_code(code)
        computer.execute()
