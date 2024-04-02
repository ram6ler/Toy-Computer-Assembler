prompt:
  .ascii "Hello, world!"
.main
  mov %a prompt
loop:
  mov %b [%a]
  jz %b done
  .char %b
  add %a %a 1
  jump loop
done:
  .line
  halt 