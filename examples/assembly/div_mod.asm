p:
  .ascii "  Input p: "
d:
  .ascii "  Input d: "
q:
  .ascii " Quotient: "
r:
  .ascii "Remainder: "

print:
  mov %5 [%8]
  jz %5 done_print
  .char %5
  add %8 %8 %1
  jmp print
done_print:
  ret %9

.main
  mov %1 1
  mov %8 p
  proc %9 print
  .input %a
  mov %8 d
  proc %9 print
  .input %b
  mov %c 0
  mov %d 0
loop:
  jz %a done
  sub %a %a %1
  add %d %d %1
  xor %0 %d %b
  jp %0 loop
  add %c %c %1
  mov %d 0
  jmp loop
done:
  mov %8 q
  proc %9 print
  .den %c
  .line
  mov %8 r
  proc %9 print
  .den %d
  .line
  halt