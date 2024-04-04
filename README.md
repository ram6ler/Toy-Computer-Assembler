# Toy Computer & Assembler

Welcome to *Toy Computer & Assembler*, a simple virtual computer and assembler that can be used as an educational tool when introducing students to computer architecture, machine language and assembly.

*Toy Computer* is a Python implementation of an imaginary computer described in chapter 6 of:

> **Sedgewick, R. & Wayne, K. (2017)** *Computer Science: An Interdisciplinary Approach.* Pearson Education.

With the 2-byte value in the CIR interpreted as either four nibbles `opcode d s t` or two nibbles and a byte `opcode d addr`, the machine instructions available are:

|Opcode|Description|Pseudocode|
|:--:|:--|:--|
|0|halt|-|
|1|add|R[d] <- R[s] + R[t]|
|2|subtract|R[d] <- R[s] - R[t]|
|3|bitwise and|R[d] <- R[s] & R[t]|
|4|bitwise xor|R[d] <- R[s] ^ R[t]|
|5|left shift|R[d] <- R[s] << R[t]|
|6|right shift|R[d] <- R[s] >> R[t]|
|7|load address|R[d] <- addr|
|8|load|R[d] <- M[addr]|
|9|store|

## Input / output

Some IO functionality has been associated with a few memory addresses so that an element of user interaction can be implemented more conveniently:

### Special Load Addresses

Loading data (instructions 8 and A) to register d from addresses F0 and FA has the following effects:

|Address|Effect|
|:--:|:--|
|F0|Stores data input via stdin to d.|
|FA|Loads a random word to d.|
|FB|Stores a string input via stdin to memory starting at address in d.|

### Special Store Addresses

Storing data (instructions 9 and B) from register d to addressed F1 to F9 has the following effects.

|Address|Effect|
|:--:|:--|
|F1|Writes binary value in d to stdout.|
|F2|Writes octal value in d to stdout.|
|F3|Writes hexadecimal value in d to stdout.|
|F4|Writes denary value in d to stdout.|
|F5|Writes value in d to stdout as an ascii character.|
|F6|Writes a new line to stdout.|
|F7|Outputs the value in d as a binary pattern.|
|F8|Outputs the state of the computer.|
|F9|Outputs the state of the computer in compilable machine language.|

## Toy Machine Language

Programs can be written in machine language (as defined by S & W). For example, the file *fibonacci.mc* contains the machine language code:

```text
PC: 00
00: 7001
01: 8AF0
02: 7B00
03: 7C01
04: 9BF4
05: 9BF6
06: 1DBC
07: 7B00
08: 1BBC
09: 7C00
0A: 1CCD
0B: 2AA0
0C: DA04
0D: 0000
```

When executed, the program waits for an integer input from stdin and then outputs that number of terms of the Fibonacci sequence:

```text
10
0
1
1
2
3
5
8
13
21
34
```

## Toy Assembly

Programs can also be written in a simple assembly language with the following instructions available:

### Program Control

|Instruction|Example|Effect|
|:--|:--|:--|
|halt|halt|Halts execution of the program.|
|jz d a|jz %0 0xA0|Jumps to address a if value in register d is zero.|
|jz d l|jz %0 end|Jumps to address marked by label l if value in register d is zero.|
|jp d a|jp %0 0xA0|Jumps to address a if value in register d is positive.|
|jp d l|jp %0 end|Jumps to address marked by label l if value in register d is positive.|
|jmp a|jmp 0xA0|Jumps to address a.|
|jmp l|jmp loop|Jumps to address marked by label l.|
|proc d a|proc %0 0xA0|Stores current position to register d and jumps to address a.|
|proc d l|proc %0 print|Stores current position to register d and jumps to address marked by label l.|
|ret d|ret %0|Jumps to address in register d.|

### Moving Data

|Instruction|Example|Effect|
|:--|:--|:--|
|ld d v|ld %0 0x89AB|Loads value v to register d.|
|ld d a|ld %0 [0xA0]|Loads value at address a to register d.|
|ld d l|ld %0 loop|Loads address marked by label l to register d.|
|ld d la|ld %0 [x]|Loads value in address marked by label l to register d.|
|ld d p|ld %0 [%1]|Loads value at address in register p to register d.|
|st a s|st [0xA0] %0|Stores value in register s to address a.|
|st p s|st [%0] %1|Stores value in register s to address in register p.|
|mov d s|move %0 %1|Moves (copies) value in register s to register d.|

### Operations

For the binary operations:

* *add*
* *sub*
* *and*
* *or*
* *xor*
* *lsh* (left shift)
* *rsh* (right shift)

|Instruction|Example|Effect|
|:--|:--|:--|
|(op) d s t|add %0 %1 %2|Performs the operation on the values in registers s and t and stores the result in register d.|
|(op) d s v|add %0 %1 42|Performs the operation on the the value in register s and value v and stores the result in register d.|
|(op) d s|add %0 %1|Performs the operation on the values in registers d and s and stores the result back in register d.|
|(op) d v|add %0 1|Performs the operation on the value in register d and value v and stores the result back in register d.|

For the unary operation *not*:

|Instruction|Example|Effect|
|:--|:--|:--|
|not d s|not %0 %1|Stores the negation of the value in register s to register d.|
|not d v|not %0 0x89AB|Stores the negation of value v to register d.|

### Special Instructions

|Instruction|Example|Effect|
|:--|:--|:--|
|.main|.main|Indicates the start point of the program.|
|.word|.word|Adds an empty register to the memory.|
|.dump|.dump|Outputs data in registers and memory.|
|.state|.state|Outputs data in registers and memory as machine code.|
|.data|.data 1, 0xAB12, 0b101|Stores data to memory.|
|.ascii|.ascii "Hello, world!"|Stores ascii values of characters (then zero) to memory.|
|.line|.line|Outputs a new line.|
|.char s|.char %0|Outputs value in register s as an ascii character.|
|.bin s|.bin %0|Outputs value in register s as binary.|
|.oct s|.oct %0|Outputs value in register s as octal.|
|.den s|.den %0|Outputs value in register s as denary.|
|.hex s|.hex %0|Outputs value in register s as hexadecimal.|
|.rand d|.random %0|Stores random value to register d.|
|.input d|.input %0|Stores input value to register d.|
|.string d|.string %0|Stores input string as ascii values to memory starting at address in d.|

For example, the file *smiley.asm* contains the following assembly:

```text
prompt:
  .ascii "How are you feeling (1: happy, 2: neutral, 3: sad)? "

.main
  ld %0 prompt
loop_prompt:
  ld %1 [%0]
  jz %1 done_prompt
  .char %1
  add %0 1
  jmp loop_prompt
done_prompt:
  .input %0
  and %0 0x000F
  jp %0 okay
  halt
okay:
  .line
  sub %0 1
  ld %a happy
  ld %b 16
find_face:
  jz %0 draw_face
  add %a 16
  sub %0 1
  jmp find_face
draw_face:
  jz %b end
  ld %c [%a]
  .pattern %c
  add %a 1
  sub %b 1
  jmp draw_face
end:
  .line
  halt

happy:
  .data 0x07E0, 0x1818, 0x2004, 0x4002
  .data 0x4812, 0x8811, 0x8001, 0x8001
  .data 0x8811, 0x8811, 0x8421, 0x43C2
  .data 0x4002, 0x2004, 0x1818, 0x07E0

neutral:
  .data 0x07E0, 0x1818, 0x2004, 0x4002
  .data 0x4002, 0x8811, 0x8811, 0x8001
  .data 0x8001, 0x8001, 0x8001, 0x4FF2
  .data 0x4002, 0x2004, 0x1818, 0x07E0

sad:
  .data 0x07E0, 0x1818, 0x2004, 0x4002
  .data 0x4422, 0x8C31, 0x8001, 0x9009
  .data 0x83C1, 0x97E9, 0x87E1, 0x57EA
  .data 0x47E2, 0x2004, 0x1818, 0x07E0

```

When executed, the program asks the user how he or she is feeling and then draws a corresponding picture to the terminal:

```text
How are you feeling (1: happy, 2: neutral, 3: sad)? 1

     ██████     
   ██      ██   
  █          █  
 █            █ 
 █  █      █  █ 
█   █      █   █
█              █
█              █
█   █      █   █
█   █      █   █
█    █    █    █
 █    ████    █ 
 █            █ 
  █          █  
   ██      ██   
     ██████     

```

## Installing

Install directly from this repository:

```text
pip install git+https://github.com/ram6ler/Toy-Computer-Assembler.git@main
```

### To Use as a Module

The folder *toy* can be used as a module to compile and execute programs written in machine language or assembly. For example, to compile and run the above, we could use:

```text
python -m toy examples/machine/fibonacci.mc
```

```text
python -m toy examples/assembly/smiley.asm
```

(The module looks for the substring .asm in the file name to determine how to compile the file.)

### To Use as a Library

Either feed the PC, RAM and register data directly to the computer...

```py
from toy import ToyComputer

computer = ToyComputer()

computer.set_state(
    pc=0x00,
    ram=[
        0x7001,
        0x8AF0,
        0x7B00,
        0x7C01,
        0x9BF4,
        0x9BF6,
        0x1DBC,
        0x7B00,
        0x1BBC,
        0x7C00,
        0x1CCD,
        0x2AA0,
        0xDA04,
        0x0000,
    ],
    registers=[],
)

computer.run()
```

... or compile machine language...

```py
from toy import ToyComputer

computer = ToyComputer()

computer.compile_machine_language(
    """
    PC: 00
    00: 7001
    01: 8AF0
    02: 7B00
    03: 7C01
    04: 9BF4
    05: 9BF6
    06: 1DBC
    07: 7B00
    08: 1BBC
    09: 7C00
    0A: 1CCD
    0B: 2AA0
    0C: DA04
    0D: 0000
    """
)

computer.run()
```

... or compile assembly:

```py
from toy import ToyComputer, assemble

pc, ram = assemble(
    r"""
    prompt:
      .ascii "What is your name? "
    greet:
      .ascii "Hello, "
    exclaim:
      .ascii "!"

    print:
      ld %b [%a]
      jz %b done_print
      .char %b
      add %a 1
      jmp print
    done_print:
      ret %0

    .main
      ld %a prompt
      proc %0 print
      ld %a 0xA0
      .string %a
      ld %a greet
      proc %0 print
      ld %a 0xA0
      proc %0 print
      ld %a exclaim
      proc %0 print
      .line
      halt
    """
)

computer = ToyComputer()
computer.set_state(pc, ram)
computer.run()
```

## Thanks

Thanks for your interest in this project! Be sure to [file bugs or requests](https://github.com/ram6ler/Toy-Computer-Assembler/issues)!
