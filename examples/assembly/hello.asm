prompt:
  .ascii "What is your name? "
greet:
  .ascii "Hello, "
exclaim:
  .ascii "!"

print:
  load %b [%a]
  jz %b done_print
  .char %b
  add %a 1
  jmp print
done_print:
  ret %0

.main
  load %a prompt
  proc %0 print
  load %a 0xA0
  .string %a
  load %a greet
  proc %0 print
  load %a 0xA0
  proc %0 print
  load %a exclaim
  proc %0 print
  .line
  halt
