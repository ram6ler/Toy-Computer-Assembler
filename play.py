from toy import ToyComputer, assemble

computer = ToyComputer()

pc, ram = assemble(
    r"""
    title:
      .ascii "Fibonacci!"
    prompt:
      .ascii "Number of terms: "

    .main
      mov %0 title
      proc %a print
      .line
      mov %0 prompt
      proc %a print
      .input %0
      mov %1 0
      mov %2 1
    loop:
      jz %0 end
      sub %0 %0 1
      add %3 %1 %2
      mov %1 %2
      mov %2 %3
      .den %1
      .line
      jump loop
    end: 
      halt

    print:
      mov %1 [%0]
      jz %1 done_print
      .char %1
      add %0 %0 1
      jump print
    done_print:
      ret %a
    """
)
computer.load(pc, ram)
computer.execute()
