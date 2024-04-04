p:
  .ascii "  Numerator: "
d:
  .ascii "Denominator: "
q:
  .ascii "   Quotient: "
r:
  .ascii "  Remainder: "

print:
  ld %5 [%8]
  jz %5 done_print
  .char %5
  add %8 %1
  jmp print
done_print:
  ret %9

.main
  ld %1 1
  ld %8 p
  proc %9 print
  .input %a
  ld %8 d
  proc %9 print
  .input %b
  ld %c 0
  ld %d 0
loop:
  jz %a done
  sub %a %1
  add %d %1
  xor %0 %d %b
  jp %0 loop
  add %c %1
  ld %d 0
  jmp loop
done:
  ld %8 q
  proc %9 print
  .den %c
  .line
  ld %8 r
  proc %9 print
  .den %d
  .line
  halt