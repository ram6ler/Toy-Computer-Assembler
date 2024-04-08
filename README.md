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

Comments begin with two semicolons `;;`.

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
|proc *d* *a*|proc %0 0xA0|Stores current position to register *d* and jumps to address *a*.|
|proc *d* *l*|proc %0 print|Stores current position to register *d* and jumps to address marked by label *l*.|
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
|mov *d* *s*|move %0 %1|Moves (copies) value in register *s* to register *d*.|

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
|.rand *d*|.random %0|Stores random value to register *d*.|
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

For example, the file *smiley.asm* contains the following assembly:

```txt
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

```txt
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
python -m toy smiley.asm
```

(The module looks for the substring .asm in the file name to determine how to compile the file.)

We can also run the module without specifying a file to start a simple Toy Computer interface:

```txt
python -m toy
```

This opens an interface that allows us to load, run, edit and explore programs. Here is an example session:

```txt

.------------------------------------------.
|        _____                             |
|       |_   _|__ _  _                     |
|         | |/ _ \ || |                    |
|         |_|\___/\_, |                    |
|    ___          |__/       _             |
|   / __|___ _ __  _ __ _  _| |_ ___ _ _   |
|  | (__/ _ \ '  \| '_ \ || |  _/ -_) '_|  |
|   \___\___/_|_|_| .__/\_,_|\__\___|_|    |
|                 |_|                      |
|                           Version 0.0.1  |
'------------------------------------------'


 > load examples/assembly/hello.asm
Compiled examples/assembly/hello.asm as assembly.

hello.asm > code

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


hello.asm > run
.................................................................... Run Started
What is your name? Poptart
Hello, Poptart!

...................................................................... Run Ended

hello.asm > machine

PC: 31
R0: 0030
Ra: 001d
Re: 0001
Rf: 001e
00: 0057;    87  0000000001010111  'W'                         
01: 0068;   104  0000000001101000  'h'                         
02: 0061;    97  0000000001100001  'a'                         
03: 0074;   116  0000000001110100  't'                         
04: 0020;    32  0000000000100000  ' '                         
05: 0069;   105  0000000001101001  'i'                         
06: 0073;   115  0000000001110011  's'                         
07: 0020;    32  0000000000100000  ' '                         
08: 0079;   121  0000000001111001  'y'                         
09: 006f;   111  0000000001101111  'o'                         
0a: 0075;   117  0000000001110101  'u'                         
0b: 0072;   114  0000000001110010  'r'                         
0c: 0020;    32  0000000000100000  ' '                         
0d: 006e;   110  0000000001101110  'n'                         
0e: 0061;    97  0000000001100001  'a'                         
0f: 006d;   109  0000000001101101  'm'                         
10: 0065;   101  0000000001100101  'e'                         
11: 003f;    63  0000000000111111  '?'                         
12: 0020;    32  0000000000100000  ' '                         
14: 0048;    72  0000000001001000  'H'                         
15: 0065;   101  0000000001100101  'e'                         
16: 006c;   108  0000000001101100  'l'                         
17: 006c;   108  0000000001101100  'l'                         
18: 006f;   111  0000000001101111  'o'                         
19: 002c;    44  0000000000101100  ','                         
1a: 0020;    32  0000000000100000  ' '                         
1c: 0021;    33  0000000000100001  '!'                         
1e: ab0a; 43786  1010101100001010               R[b] <- M[R[a]]
1f: cb25; 52005  1100101100100101       if (R[b] == 0) PC <- 25
20: 9bf5; 39925  1001101111110101                 M[f5] <- R[b]
21: 7e01; 32257  0111111000000001                     R[e] <- 1
22: 1aae;  6830  0001101010101110           R[a] <- R[a] + R[e]
23: 7f1e; 32542  0111111100011110                    R[f] <- 1e
24: ef00; 61184  1110111100000000                    PC <- R[f]
25: e000; 57344  1110000000000000                    PC <- R[0]
26: 7a00; 31232  0111101000000000                     R[a] <- 0
27: f01e; 61470  1111000000011110          R[0] <- PC; PC <- 1e
28: 7aa0; 31392  0111101010100000                    R[a] <- a0
29: 8afb; 35579  1000101011111011                 R[a] <- M[fb]
2a: 7a14; 31252  0111101000010100                    R[a] <- 14
2b: f01e; 61470  1111000000011110          R[0] <- PC; PC <- 1e
2c: 7aa0; 31392  0111101010100000                    R[a] <- a0
2d: f01e; 61470  1111000000011110          R[0] <- PC; PC <- 1e
2e: 7a1c; 31260  0111101000011100                    R[a] <- 1c
2f: f01e; 61470  1111000000011110          R[0] <- PC; PC <- 1e
30: 90f6; 37110  1001000011110110                 M[f6] <- R[0]
a0: 0050;    80  0000000001010000  'P'                         
a1: 006f;   111  0000000001101111  'o'                         
a2: 0070;   112  0000000001110000  'p'                         
a3: 0074;   116  0000000001110100  't'                         
a4: 0061;    97  0000000001100001  'a'                         
a5: 0072;   114  0000000001110010  'r'                         
a6: 0074;   116  0000000001110100  't'                         


hello.asm > 14 004a
M[14] 0048 -> 004a


hello.asm > reset
Program counter reset to 26.

hello.asm > run
.................................................................... Run Started
What is your name? Poptart
Jello, Poptart!

...................................................................... Run Ended

hello.asm > dump

    R         |  RAM   _0   _1   _2   _3   _4   _5   _6   _7   _8   _9   _a   _b   _c   _d   _e   _f
    0 0030    |   0_ 0057 0068 0061 0074 0020 0069 0073 0020 0079 006f 0075 0072 0020 006e 0061 006d
    1 0000    |   1_ 0065 003f 0020 0000 004a 0065 006c 006c 006f 002c 0020 0000 0021 0000 ab0a cb25
    2 0000    |   2_ 9bf5 7e01 1aae 7f1e ef00 e000 7a00 f01e 7aa0 8afb 7a14 f01e 7aa0 f01e 7a1c f01e
    3 0000    |   3_ 90f6 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
    4 0000    |   4_ 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
    5 0000    |   5_ 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
    6 0000    |   6_ 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
    7 0000    |   7_ 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
    8 0000    |   8_ 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
    9 0000    |   9_ 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
    a 001d    |   a_ 0050 006f 0070 0074 0061 0072 0074 0000 0000 0000 0000 0000 0000 0000 0000 0000
    b 0000    |   b_ 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
    c 0000    |   c_ 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
    d 0000    |   d_ 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
    e 0001    |   e_ 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
    f 001e    |   f_ 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000

    PC:   31
    IR: 0000
Pseudo: halt


hello.asm > quit


So long!

```

### To Use as a Library

The library can be imported to a Python script.

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
