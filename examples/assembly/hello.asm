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
