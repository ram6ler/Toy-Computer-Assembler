# Toy Computer & Assembler

Welcome to *Toy Computer & Assembler*, a simple virtual computer and assembler that can be used as an educational tool when introducing students to computer architecture, machine language and assembly.

*Toy Computer* is a Python implementation of an imaginary computer described in chapter 6 of:

> **Sedgewick, R. & Wayne, K. (2017)** *Computer Science: An Interdisciplinary Approach.* Pearson Education.

Some IO functionality has been associated with a few memory addresses so that an element of user interaction can be implemented more conveniently:

## Special Load Addresses

Loading data (instructions 8 and A) to register d from addresses F0 and FA has the following effects:

|Address|Effect|
|:--:|:--|
|F0|Stores data input via stdin to d.|
|FA|Loads a random word to d.|
|FB|Stores a string input via stdin to memory starting at address in d.|

## Special Store Addresses

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

## Machine Language

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

|Instruction|Example|Effect|
|:--|:--|:--|
|halt|halt|Halts execution of the program.|
|not d t|not %a %b|Stores bitwise not of value in register t to register d.|
|and d s t|and %a %b %c|Stores bitwise and of values stored in registers s and t in register d.|
|and d s v|and %a %b 0x89AB|Stores bitwise and of value stored in register s and value v in register d. |
|or d s t|or %a %b %c|Stores bitwise or of values stored in registers s and t in register d.|
|or d s v|or %a %b 0x89AB|Stores bitwise or of value stored in register s and value v in register d. |
|xor d s t|xor %a %b %c|Stores bitwise xor of values stored in registers s and t to register d.|
|xor d s v|xor %a %b 0x89AB|Stores bitwise xor of value stored in register s and value v to register d. |
|lsh d s t|lsh %a %b %c|Stores value in register s left shifted by value stored in register t to register d.|
|lsh d s v|lsh %a %b 3|Stores value in register s left shifted by value v to register d.|
|rsh d s t|rsh %a %b %c|Stores value in register s right shifted by value stored in register t to register d.|
|rsh d s v|rsh %a %b 3|Stores value in register s right shifted by value v to register d.|
|add d s t|add %a %b %c|Stores sum of values stored in registers s and t to register d.|
|add d s v|add %a %b 0x89AB|Stores sum of value stored in register s and value v to register d. |
|sub d s t|sub %a %b %c|Stores value stored in register s minus value stored in register t to register d.|
|sub d s v|sub %a %b 0x89AB|Stores value stored in register s minus value v to register d.|
|mov d l|mov %0 loop|Stores address marked by label l to register d.|
|mov d v|mov %0 0x89AB|Stores value v to register d.|
|mov d a|mov %0 [0xA0]|Copies value at address a to register d.|
|mov a s|mov [0xA0] %0|Copies value from register s to address a.|
|mov la d|mov [x] %0|Copies value in register d to address marked by label l.|
|mov d la|mov %0 [x]|Copies value in address marked by label l to register d.|
|mov d s|mov %0 %1|Copies value in register s to register d.|
|mov d p|mov %0 [%1]|Copies value at address stored in register p to register d.|
|mov p s|mov [%0] %1|Copies value in register s to address stored in register p.|
|jz d a|jz %0 0xA0|Jumps to address a if value in register d is zero.|
|jz d l|jz %0 end|Jumps to address marked by label l if value in register d is zero.|
|jp d a|jp %0 0xA0|Jumps to address a if value in register d is positive.|
|jp d l|jp %0 end|Jumps to address marked by label l if value in register d is positive.|
|jmp a|jmp 0xA0|Jumps to address a.|
|jmp l|jmp loop|Jumps to address marked by label l.|
|proc d a|proc %0 0xA0|Stores current position to register d and jumps to address a.|
|proc d l|proc %0 print|Stores current position to register d and jumps to address marked by label l.|
|ret d|ret %0|Jumps to address stored in register d.|

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
  mov %0 prompt
loop_prompt:
  mov %1 [%0]
  jz %1 done_prompt
  .char %1
  add %0 %0 1
  jmp loop_prompt
done_prompt:
  .input %0
  and %0 %0 0x000F
  jp %0 okay
  halt

okay:
  .line
  sub %0 %0 1
  mov %a happy
  mov %b 16

find_face:
  jz %0 draw_face
  add %a %a 16
  sub %0 %0 1
  jmp find_face

draw_face:
  jz %b end
  mov %c [%a]
  .pattern %c
  add %a %a 1
  sub %b %b 1
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

## To Use as a Module

The folder *toy* can be used as a module to compile and execute programs written in machine language or assembly. For example, to compile and run the above, we could use:

```text
python -m toy examples/machine/fibonacci.mc
```

```text
python -m toy examples/assembly/smiley.asm
```

(The module looks for the substring .asm in the file name to determine how to compile the file.)

## To Use as a Library

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
    title:
      .ascii "Fibonacci!"
    prompt:
      .ascii "Number of terms: "

    .main
      mov %0 title
      proc %a print
      .line
      mov %0 prompt
      proc %a print
      .input %0
      mov %1 0
      mov %2 1
    loop:
      jz %0 end
      sub %0 %0 1
      add %3 %1 %2
      mov %1 %2
      mov %2 %3
      .den %1
      .line
      jmp loop
    end: 
      halt

    print:
      mov %1 [%0]
      jz %1 done_print
      .char %1
      add %0 %0 1
      jmp print
    done_print:
      ret %a
    """
)

computer = ToyComputer()
computer.set_state(pc, ram)
computer.run()
```

## Thanks

Thanks for your interest in this project! Be sure to [file bugs or requests](https://github.com/ram6ler/Toy-Computer-Assembler/issues)!
