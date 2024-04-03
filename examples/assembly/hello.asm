prompt:
  .ascii "What is your name? "
greet:
  .ascii "Hello, "
exclaim:
  .ascii "!"

print:
  mov %b [%a]
  jz %b done_print
  .char %b
  add %a %a 1
  jmp print
done_print:
  ret %0

.main
  mov %a prompt
  proc %0 print
  mov %a 0xA0
  .string %a
  mov %a greet
  proc %0 print
  mov %a 0xA0
  proc %0 print
  mov %a exclaim
  proc %0 print
  .line
  halt
