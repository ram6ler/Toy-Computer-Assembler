     prompt: .ascii "How are you feeling today (1: happy, 2: neutral, 3: sad)? "
            
             .main 
             ld %0 prompt
            
loop_prompt: ld %1 [%0]
             jz %1 done_prompt
             .char %1
             add %0 1
             jmp loop_prompt
            
done_prompt: .input %0
             and %0 0x0003
             jp %0 okay
             halt 
            
       okay: .line 
             sub %0 1
             ld %a happy
             ld %b 16
            
  find_face: jz %0 draw_face
             add %a 16
             sub %0 1
             jmp find_face
            
  draw_face: jz %b end
             ld %c [%a]
             .pattern %c
             add %a 1
             sub %b 1
             jmp draw_face
            
        end: .line 
             halt 
            
      happy: .data 0x07E0, 0x1818, 0x2004, 0x4002
             .data 0x4812, 0x8811, 0x8001, 0x8001
             .data 0x8811, 0x8811, 0x8421, 0x43C2
             .data 0x4002, 0x2004, 0x1818, 0x07E0
            
    neutral: .data 0x07E0, 0x1818, 0x2004, 0x4002
             .data 0x4002, 0x8811, 0x8811, 0x8001
             .data 0x8001, 0x8001, 0x8001, 0x4FF2
             .data 0x4002, 0x2004, 0x1818, 0x07E0
            
        sad: .data 0x07E0, 0x1818, 0x2004, 0x4002
             .data 0x4422, 0x8C31, 0x8001, 0x9009
             .data 0x83C1, 0x97E9, 0x87E1, 0x57EA
             .data 0x47E2, 0x2004, 0x1818, 0x07E0
