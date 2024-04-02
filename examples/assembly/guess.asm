intro_1:
  .ascii "Welcome to guess!"
intro_2:
  .ascii "I'm thinking of a number from 0 to 255."
intro_3:
  .ascii "Try to guess it!"
guess:
  .ascii "Guess number: "
prompt:
  .ascii "What is your guess? "
too_high:
  .ascii "Too high!"
too_low:
  .ascii "Too low!"
correct_1:
  .ascii "You got it in "
correct_2:
  .ascii " moves! Great job!"
  
print:
  mov %c [%a]
  jz %c done_print
  .char %c
  add %a %a 1
  jump print
done_print:
  ret %b

.main
  mov %a intro_1
  proc %b print
  .line
  mov %a intro_2
  proc %b print
  .line
  mov %a intro_3
  proc %b print
  .line
  .rand %0
  and %0 %0 0x00FF
  mov %1 0
loop:
  add %1 %1 1
  mov %a guess
  proc %b print
  .den %1
  .line
  mov %a prompt
  proc %b print
  .input %2
  xor %3 %0 %2
  jz %3 if_correct
  mov %4 %0
compare:
  sub %2 %2 1
  jz %2 if_too_low
  sub %4 %4 1
  jz %4 if_too_high
  jump compare
if_too_low:
  mov %a too_low
  proc %b print
  .line
  jump loop
if_too_high:
  mov %a too_high
  proc %b print
  .line
  jump loop
if_correct:
  mov %a correct_1
  proc %b print
  .den %1
  mov %a correct_2
  proc %b print
  .line
  halt