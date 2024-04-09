prompt:
  .ascii "Input "
prompt_a:
  .ascii "a"
prompt_d:
  .ascii "d"
prompt_n:
  .ascii "n"
prompt_end:
  .ascii ": "

a_:
  .word
d_:
  .word
n_:
  .word

print:
  ld %1 [%0]
  jz %1 done_print
  .char %1
  add %0 1
  jmp print
done_print:
  ret %a

input:
  ld %0 prompt
  proc %a print
  mv %0 %2
  proc %a print
  ld %0 prompt_end
  proc %a print
  .input %b
  st [%3] %b
  ret %4

.main
  ld %2 prompt_a
  ld %3 a_
  proc %4 input
  ld %2 prompt_d
  ld %3 d_
  proc %4 input
  ld %2 prompt_n
  ld %3 n_
  proc %4 input
  proc %4 display
  halt

display:
  ld %0 [a_]
  ld %1 [d_]
  ld %2 [n_]
loop_display:
  jz %2 done_display
  .den %0
  .line
  add %0 %1
  sub %2 1
  jmp loop_display
done_display:
  ret %4
