      prompt_1: .ascii "Input starting row: "
      prompt_2: .ascii "How many rows? "
               
display_prompt: ld %b [%a]
                jz %b done_display
                .char %b
                add %a 1
                jmp display_prompt
  done_display: ret %c
               
                .main 
                ld %a prompt_1
                call %c display_prompt
                .input %0
                ld %a prompt_2
                call %c display_prompt
                .input %1
                .line 
                .pattern %0
               
      loop_row: ld %2 0xF
                ld %b 0
               
      loop_bit: mv %3 %0
                mv %c %2
                sub %c 1
                rsh %3 %c
                and %3 0b111
                xor %4 %3 0b110
                jz %4 add_bit
                xor %4 %3 0b100
                jz %4 add_bit
                xor %4 %3 0b011
                jz %4 add_bit
                xor %4 %3 0b001
                jz %4 add_bit
                jmp done_loop_bit
               
       add_bit: ld %4 1
                lsh %4 %2
                or %b %4
               
 done_loop_bit: sub %2 1
                jp %2 loop_bit
                .pattern %b
                mv %0 %b
                sub %1 1
                jp %1 loop_row
                halt 
