       greet: .ascii "Hello! What is your name? "
         say: .ascii "Nice to meet you, "
     exclaim: .ascii "!"
     mistake: .ascii "Whoops! I guess I got it backwards!"
         ask: .ascii "Do you prefer it that way (y/n)? "
         yes: .ascii "I knew you would!"
          no: .ascii "Sorry to hear that!"
         bye: .ascii "Good bye!"
             
       print: ld %1 [%0]
              jz %1 done_print
              .char %1
              add %0 1
              jmp print
  done_print: ret %a
             
              .main 
              ld %0 greet
              call %a print
              ld %0 user_input
              .string %0
              ld %0 say
              call %a print
              ld %0 user_input
              mv %1 %0
             
    find_end: ld %2 [%1]
              jz %2 found_end
              add %1 1
              jmp find_end
             
   found_end: ld %2 [%1]
              .char %2
              xor %2 %1 %0
              jz %2 backwards
              sub %1 1
              jmp found_end
             
   backwards: ld %0 exclaim
              call %a print
              .line 
              ld %0 mistake
              call %a print
              .line 
              ld %0 ask
              call %a print
              ld %0 user_input
              .string %0
              ld %0 [user_input]
              ld %1 0x79
              xor %2 %1 %0
              jz %2 user_prefers
              ld %0 no
              call %a print
              jmp end
             
user_prefers: ld %0 yes
              call %a print
             
         end: .line 
              ld %0 bye
              call %a print
              .line 
              halt 
             
  user_input: .word 
