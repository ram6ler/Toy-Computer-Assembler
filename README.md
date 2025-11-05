# Toy Computer & Assembler

Welcome to *Toy Computer & Assembler*, a simple virtual computer and assembler that can be used as an educational tool when introducing students to computer architecture, machine language and assembly.

*Toy Computer* is a Python implementation of an imaginary computer described in chapter 6 of:

> **Sedgewick, R. & Wayne, K. (2017)**
> *Computer Science: An Interdisciplinary Approach.* Pearson Education.

The computer has a word size of two bytes, sixteen general purpose one-word registers (named 0 to F), and 256 addressable words in memory. A one-byte program counter (PC) stores the address of the next instruction; a one-word instruction register (CIR) stores the next instruction. With the word value in the CIR interpreted as either four nibbles `opcode d s t` or two nibbles and a byte `opcode d addr`, the machine instructions available are:

|Opcode|Description|Pseudocode|
|:--:|:--|:--|
|0|halt|-|
|1|add|R[d] ← R[s] + R[t]|
|2|subtract|R[d] ← R[s] - R[t]|
|3|bitwise and|R[d] ← R[s] & R[t]|
|4|bitwise xor|R[d] ← R[s] ^ R[t]|
|5|left shift|R[d] ← R[s] << R[t]|
|6|right shift|R[d] ← R[s] >> R[t]|
|7|load address|R[d] ← addr|
|8|load|R[d] ← M[addr]|
|9|store|M[addr] ← R[d]|
|A|load indirect|R[d] ← M[R[t]]|
|B|store indirect|M[R[t]] ← R[d]|
|C|branch zero|if R[d] == 0 PC ← addr|
|D|branch positive|if R[d] > 0 PC ← addr|
|E|jump register|PC ← R[d]|
|F|jump & link|R[d] ← PC; PC ← addr|

## Input / output

Some IO functionality has been associated with a few memory addresses so that an element of user interaction can be implemented more conveniently:

### Special Load Addresses

Loading data (instructions 8 and A) to register *d* from addresses F0 and FA has the following effects:

|Address|Effect|
|:--:|:--|
|F0|Stores data input via stdin to *d*.|
|FA|Loads a random word to *d*.|
|FB|Stores a string input via stdin to memory starting at address in *d*.|

### Special Store Addresses

Storing data (instructions 9 and B) from register *d* to addressed F1 to F9 has the following effects.

|Address|Effect|
|:--:|:--|
|F1|Writes binary value in *d* to stdout.|
|F2|Writes octal value in *d* to stdout.|
|F3|Writes hexadecimal value in *d* to stdout.|
|F4|Writes denary value in *d* to stdout.|
|F5|Writes value in *d* to stdout as an ascii character.|
|F6|Writes a new line to stdout.|
|F7|Outputs the value in *d* as a binary pattern.|
|F8|Outputs the state of the computer.|
|F9|Outputs the state of the computer in compilable machine language.|

## Toy Machine Language

Programs can be written in machine language (as defined by S & W). For example, the file *fibonacci.mc* contains the machine language code:

```txt
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

```txt
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

### Comments

Comments begin with a semicolon.

### Labels

|Instruction|Example|Effect|
|:--|:--|:--|
|.main|.main|Indicates the start point of the program.|
|(label):|loop:|Creates a mnemonic for an address.|

### Program Control

|Instruction|Example|Effect|
|:--|:--|:--|
|halt|halt|Halts execution of the program.|
|jz *d* *a*|jz %0 0xA0|Jumps to address *a* if value in register *d* is zero.|
|jz *d* *l*|jz %0 end|Jumps to address marked by label *l* if value in register *d* is zero.|
|jp *d* *a*|jp %0 0xA0|Jumps to address *a* if value in register *d* is positive.|
|jp *d* *l*|jp %0 end|Jumps to address marked by label *l* if value in register *d* is positive.|
|jmp *a*|jmp 0xA0|Jumps to address *a*.|
|jmp *l*|jmp loop|Jumps to address marked by label *l*.|
|call *d* *a*|call %0 0xA0|Stores current position to register *d* and jumps to address *a*.|
|call *d* *l*|call %0 print|Stores current position to register *d* and jumps to address marked by label *l*.|
|ret *d*|ret %0|Jumps to address in register *d*.|

### Moving Data

|Instruction|Example|Effect|
|:--|:--|:--|
|ld *d* v|ld %0 0x89AB|Loads value v to register *d*.|
|ld *d* *a*|ld %0 [0xA0]|Loads value at address *a* to register *d*.|
|ld *d* *l*|ld %0 loop|Loads address marked by label *l* to register *d*.|
|ld *d* la|ld %0 [x]|Loads value in address marked by label *l* to register *d*.|
|ld *d* *p*|ld %0 [%1]|Loads value at address in register *p* to register *d*.|
|st *a* *s*|st [0xA0] %0|Stores value in register *s* to address *a*.|
|st *p* *s*|st [%0] %1|Stores value in register *s* to address in register *p*.|
|st *l* *s*|st x %1|Stores value in register *s* to address marked by label *l*.|
|mv *d* *s*|mv %0 %1|Moves (copies) value in register *s* to register *d*.|

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
|(op) *d* *s* *t*|add %0 %1 %2|Performs the operation on the values in registers *s* and *t* and stores the result in register *d*.|
|(op) *d* *s* v|add %0 %1 42|Performs the operation on the the value in register *s* and value v and stores the result in register *d*.|
|(op) *d* *s*|add %0 %1|Performs the operation on the values in registers *d* and *s* and stores the result back in register *d*.|
|(op) *d* v|add %0 1|Performs the operation on the value in register *d* and value v and stores the result back in register *d*.|

For the unary operation *not*:

|Instruction|Example|Effect|
|:--|:--|:--|
|not *d* *s*|not %0 %1|Stores the negation of the value in register *s* to register *d*.|
|not *d* v|not %0 0x89AB|Stores the negation of value v to register *d*.|

### Data

|Instruction|Example|Effect|
|:--|:--|:--|
|.word|.word|Adds an empty register to the memory.|
|.data|.data 1, 0xAB12, 0b101|Stores data to memory.|
|.ascii|.ascii "Hello, world!"|Stores ascii values of characters (then zero) to memory.|

### Input

|Instruction|Example|Effect|
|:--|:--|:--|
|.rand *d*|.rand %0|Stores random value to register *d*.|
|.input *d*|.input %0|Stores input value to register *d*.|
|.string *d*|.string %0|Stores input string as ascii values to memory starting at address in *d*.|

### Output

|Instruction|Example|Effect|
|:--|:--|:--|
|.dump|.dump|Outputs data in registers and memory.|
|.state|.state|Outputs data in registers and memory as machine code.|
|.line|.line|Outputs a new line.|
|.char *s*|.char %0|Outputs value in register *s* as an ascii character.|
|.bin *s*|.bin %0|Outputs value in register *s* as binary.|
|.oct *s*|.oct %0|Outputs value in register *s* as octal.|
|.den *s*|.den %0|Outputs value in register *s* as denary.|
|.hex *s*|.hex %0|Outputs value in register *s* as hexadecimal.|

### Notes

* For some assembly instructions, registers D, E and F are used for scratch work; in general, these registers should be avoided when programming in assembly.

### Example

For example, the file *hello.asm* contains the following assembly:

```txt
       greet: .ascii "Hello! What is your name? "
         say: .ascii "Nice to meet you, "
     exclaim: .ascii "!"
     mistake: .ascii "Whoops! I guess I got it backwards!"
         ask: .ascii "Do you prefer it that way (y/n)? "
         yes: .ascii "I knew you would!"
          no: .ascii "Sorry to hear that!"
         bye: .ascii "Good bye!"
             
       print: ld %1 [%0]
              jz %1 done_print
              .char %1
              add %0 1
              jmp print
  done_print: ret %a
             
              .main 
              ld %0 greet
              call %a print
              ld %0 user_input
              .string %0
              ld %0 say
              call %a print
              ld %0 user_input
              mv %1 %0
             
    find_end: ld %2 [%1]
              jz %2 found_end
              add %1 1
              jmp find_end
             
   found_end: ld %2 [%1]
              .char %2
              xor %2 %1 %0
              jz %2 backwards
              sub %1 1
              jmp found_end
             
   backwards: ld %0 exclaim
              call %a print
              .line 
              ld %0 mistake
              call %a print
              .line 
              ld %0 ask
              call %a print
              ld %0 user_input
              .string %0
              ld %0 [user_input]
              ld %1 0x79
              xor %2 %1 %0
              jz %2 user_prefers
              ld %0 no
              call %a print
              jmp end
             
user_prefers: ld %0 yes
              call %a print
             
         end: .line 
              ld %0 bye
              call %a print
              .line 
              halt 
             
  user_input: .word 
```

Example run when compiled and executed:

```txt
Hello! What is your name? Poptart
Nice to meet you, tratpoP!
Whoops! I guess I got it backwards!
Do you prefer it that way (y/n)? y
I knew you would!
Good bye!
```

## Installing

Install directly from this repository (for Python ≥ 3.12):

```txt
pip install git+https://github.com/ram6ler/Toy-Computer-Assembler.git@main
```

### To Use as a Module

The library can be used as a module to compile and execute programs written in machine language or assembly. For example, to compile and run the above examples, we could use:

```txt
python -m toy fibonacci.mc
```

```txt
python -m toy hello.asm
```

(The module looks for the substring .asm in the file name to determine how to compile the file.)

We can also run the module without specifying a file to start a simple Toy Computer interface:

```txt
python -m toy
```

This opens an interface that allows us to load, run, edit and explore programs. Here is an example session:

```txt

       _____
      |_   _|__ _  _ 
 .------| |/ _ \ || |---------------------.
 |      |_|\___/\_, |                     |
 |   ___        |__/         _            |
 |  / __|___ _ __  _ __ _  _| |_ ___ _ _  |
 '-| (__/ _ \ '  \| '_ \ || |  _/ -_) '_|-'
    \___\___/_|_|_| .__/\_,_|\__\___|_|
                  |_|
        

 
 > load examples/assembly/hello.asm

Address Mappings:

  greet: 00
  say: 1b
  exclaim: 2e
  mistake: 30
  ask: 54
  yes: 76
  no: 88
  bye: 9c
  print: a6
  done_print: ad
  find_end: b7
  found_end: bd
  backwards: c5
  user_prefers: d7
  end: d9
  user_input: de

Compiled examples/assembly/hello.asm as assembly.
Program counter: ae
 
hello.asm > dump

    R         |  RAM   _0   _1   _2   _3   _4   _5   _6   _7   _8   _9   _a   _b   _c   _d   _e   _f
    0 0000    |   0_ 0048 0065 006c 006c 006f 0021 0020 0057 0068 0061 0074 0020 0069 0073 0020 0079
    1 0000    |   1_ 006f 0075 0072 0020 006e 0061 006d 0065 003f 0020 0000 004e 0069 0063 0065 0020
    2 0000    |   2_ 0074 006f 0020 006d 0065 0065 0074 0020 0079 006f 0075 002c 0020 0000 0021 0000
    3 0000    |   3_ 0057 0068 006f 006f 0070 0073 0021 0020 0049 0020 0067 0075 0065 0073 0073 0020
    4 0000    |   4_ 0049 0020 0067 006f 0074 0020 0069 0074 0020 0062 0061 0063 006b 0077 0061 0072
    5 0000    |   5_ 0064 0073 0021 0000 0044 006f 0020 0079 006f 0075 0020 0070 0072 0065 0066 0065
    6 0000    |   6_ 0072 0020 0069 0074 0020 0074 0068 0061 0074 0020 0077 0061 0079 0020 0028 0079
    7 0000    |   7_ 002f 006e 0029 003f 0020 0000 0049 0020 006b 006e 0065 0077 0020 0079 006f 0075
    8 0000    |   8_ 0020 0077 006f 0075 006c 0064 0021 0000 0053 006f 0072 0072 0079 0020 0074 006f
    9 0000    |   9_ 0020 0068 0065 0061 0072 0020 0074 0068 0061 0074 0021 0000 0047 006f 006f 0064
    a 0000    |   a_ 0020 0062 0079 0065 0021 0000 a100 c1ad 91f5 7e01 100e 7fa6 ef00 ea00 7000 faa6
    b 0000    |   b_ 70de 80fb 701b faa6 70de 7100 1110 a201 c2bd 7e01 111e 7fb7 ef00 a201 92f5 4210
    c 0000    |   c_ c2c5 7e01 211e 7fbd ef00 702e faa6 90f6 7030 faa6 90f6 7054 faa6 70de 80fb 80de
    d 0000    |   d_ 7179 4210 c2d7 7088 faa6 7fd9 ef00 7076 faa6 90f6 709c faa6 90f6 0000 0000 0000
    e 0000    |   e_ 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
    f 0000    |   f_ 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000

    PC:   ae
    IR: 7000
Pseudo: R[0] <- 0

 
hello.asm > run
.................................................................... Run Started
Hello! What is your name? Poptart
Nice to meet you, tratpoP!
Whoops! I guess I got it backwards!
Do you prefer it that way (y/n)? y
I knew you would!
Good bye!

...................................................................... Run Ended
 
hello.asm > 00: 004a
M[00] 0048 -> 004a

 
hello.asm > pc: ae
PC <- ae
 
hello.asm > run
.................................................................... Run Started
Jello! What is your name? Hahaha!
Nice to meet you, !ahahaH!
Whoops! I guess I got it backwards!
Do you prefer it that way (y/n)? n
Sorry to hear that!
Good bye!

...................................................................... Run Ended
 
hello.asm > quit


So long!

```

### To Use as a Library

The library can be imported to a Python script.

We can set the program counter and memory values directly...

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

assembled = assemble(
    code=r"""
    
    prompt: .ascii "What is your name? "
     greet: .ascii "Hello, "
   exclaim: .ascii "!"
           
     print: ld %b [%a]
            jz %b done_print
            .char %b
            add %a 1
            jmp print
done_print: ret %0
           
            .main 
            ld %a prompt
            call %0 print
            ld %a 0xA0
            .string %a
            ld %a greet
            call %0 print
            ld %a 0xA0
            call %0 print
            ld %a exclaim
            call %0 print
            .line 
            halt 
    """,
    show_addresses=False,
)

computer = ToyComputer()
computer.set_state(pc=assembled.pc, ram=assembled.words)
computer.run()
```

## Thanks

Thanks for your interest in this project! Be sure to [file bugs or requests](https://github.com/ram6ler/Toy-Computer-Assembler/issues)!
