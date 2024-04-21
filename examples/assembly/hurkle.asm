start_1:      .ascii "Hurkle!"
start_2:      .ascii "Guess where it is!"
guess_1:      .ascii "Guess "
guess_2:      .ascii " How far "
guess_3:      .ascii "? "
d_east:       .ascii "east"
d_west:       .ascii "west"
d_north:      .ascii "north"
d_south:      .ascii "south"
d_none:       .word
clue:         .ascii "Go "
end_1:        .ascii "You found it in "
end_2:        .ascii " guesses!"

g_number:     .word
h_east:       .word
h_north:      .word
g_east:       .word
g_north:      .word

              .main
              ld %1 start_1
              call %0 print
              .line
              ld %1 start_2
              call %0 print
              .line
              ld %1 h_east
              call %0 random
              ld %1 h_north
              call %0 random
              ld %1 0
              st [g_number] %1

loop_main:    .line
              ld %1 guess_1
              call %0 print
              call %0 inc_guess
              .den %1
              .line
              ld %1 guess_2
              call %0 print
              ld %1 d_east
              call %0 print
              ld %1 guess_3
              call %0 print
              ld %1 g_east
              call %0 input
              ld %1 guess_2
              call %0 print
              ld %1 d_north
              call %0 print
              ld %1 guess_3
              call %0 print
              ld %1 g_north
              call %0 input
              ld %2 [h_north]
              lsh %2 4
              ld %3 [g_north]
              lsh %3 4
              ld %4 [h_east]
              or %2 %4
              ld %4 [g_east]
              or %3 %4
              xor %4 %2 %3
              jz %4 success
              ld %1 clue
              call %0 print
              ld %a d_north
              ld %b d_south
              ld %1 [h_north]
              ld %2 [g_north]
              call %0 compare
              mv %1 %3
              call %0 print
              ld %a d_east
              ld %b d_west
              ld %1 [h_east]
              ld %2 [g_east]
              call %0 compare
              mv %1 %3
              call %0 print
             .line
             jmp loop_main

success:     .line
             ld %1 end_1
             call %0 print
             ld %1 [g_number]
             .den %1
             ld %1 end_2
             call %0 print
             .line
             halt

compare:     xor %3 %1 %2
             jp %3 not_equal
             ld %3 d_none
             ret %0
not_equal:   jz %1 less
             jz %2 more
             sub %1 1
             sub %2 1
             jmp not_equal
more:        mv %3 %a
             ret %0
less:        mv %3 %b
             ret %0  
print:       ld %2 [%1]
             jz %2 done_print
             .char %2
             add %1 1
             jmp print
done_print:  ret %0

inc_guess:   ld %1 [g_number]
             add %1 1
             st [g_number] %1
             ret %0

random:      .rand %2
             and %2 0xF
             st [%1] %2
             ret %0
 
input:       .input %2
             and %2 0xF
             st [%1] %2
             ret %0
