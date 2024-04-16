connections:
  .data 0x321, 0xed0
  .data 0xa90, 0xcb0
  .data 0xe96, 0xba8
  .data 0xcb4, 0xfdc
  .data 0xed5, 0xf42
  .data 0xf52, 0x653
  .data 0x763, 0x871
  .data 0x841, 0xa97

t_cave:
  .data 0x4361, 0x7665
  .data 0x2000
t_paths:
  .data 0x5061, 0x7468
  .data 0x7320, 0x0000
t_comma:
  .data 0x2c20, 0x0000
t_smell:
  .data 0x536d, 0x656c
  .data 0x6c20, 0x0000
t_wumpus:
  .data 0x5775, 0x6d70
  .data 0x7573, 0x2100
t_hear:
  .data 0x4865, 0x6172
  .data 0x2000
t_bats:
  .data 0x4261, 0x7473
  .data 0x2100
t_amulet:
  .data 0x416d, 0x756c
  .data 0x6574, 0x2100

print:
  ld %1 [%0]
  and %2 %1 0xFF00
  rsh %2 8
  jz %2 done_print
  .char %2
  and %2 %1 0xFF
  jz %2 done_print
  .char %2
  add %0 1
  jmp print
done_print:
  ret %a

player:
  .word
amulet:
  .word
wumpuses:
  .word
bats:
  .word
scents:
  .word
sounds:
  .word
con_1:
  .word
con_2:
  .word
con_3:
  .word

link_caves:
  ld %1 1
  ld %2 connections
  mv %3 %9
seek:
  jz %3 sought
  sub %3 %1
  add %2 %1
  jmp seek
sought:
  ld %8 [%2]
  and %2 %8 0xF
  st [con_1] %2
  rsh %8 4
  and %2 %8 0xF
  st [con_2] %2
  rsh %8 4
  st [con_3] %8
  ret %a

add_thing:
  ld %1 1
  ld %2 [%b]
  ld %6 [wumpuses]
  ld %7 [bats]
  or %6 %7
try_add_thing:
  .rand %9
  and %9 0xF
  lsh %3 %1 %9
  and %4 %6 %3
  jp %4 try_add_thing
  or %2 %3
  st [%b] %2
  call %a link_caves
  ld %1 1
  ld %2 0
  ld %3 [con_1]
  lsh %4 %1 %3
  or %2 %4
  ld %3 [con_2]
  lsh %4 %1 %3
  or %2 %4
  ld %3 [con_3]
  lsh %4 %1 %3
  or %2 %4
  ld %5 [%c]
  or %5 %2
  st [%c] %5
  ret %d

add_special:
  ld %0 [bats]
  ld %1 [wumpuses]
  or %0 %1
  ld %1 [player]
  or %0 %1
  ld %1 1
  .rand %2
  and %2 0xF
  lsh %3 %1 %2
  and %3 %0
  jp %3 add_special
  ret %a

check_cave:
  ld %2 [%4]
  and %3 %1 %2
  ret %a

.main
  ld %b wumpuses
  ld %c scents
  call %d add_thing
  call %d add_thing
  ld %b bats
  ld %c sounds
  call %d add_thing
  call %d add_thing
  call %a add_special
  st [player] %2
  call %a add_special
  st [amulet] %2

game_loop:
  .line
  ld %0 t_cave
  call %a print
  ld %9 [player]
  .den %9
  .line
  ld %0 [amulet]
  xor %0 %9
  jz %0 win
  ld %6 0
  ld %7 0
  ld %1 1
  lsh %1 %9
  ld %4 scents
  call %a check_cave
  jz %3 done_scents
  ld %6 1
done_scents:
  ld %4 sounds
  call %a check_cave
  jz %3 done_sounds
  ld %7 1
done_sounds:
  ld %4 wumpuses
  call %a check_cave
  jp %3 eaten
  ld %4 bats
  call %a check_cave
  jp %3 taken_by_bats
  ld %0 t_paths
  call %a print
  call %a link_caves
  ld %1 [con_1]
  .den %1
  ld %0 t_comma
  call %a print
  ld %1 [con_2]
  .den %1
  ld %0 t_comma
  call %a print
  ld %1 [con_3]
  .den %1
  .line
  jz %6 reported_scents
  ld %0 t_smell
  call %a print
  ld %0 t_wumpus
  call %a print
  .line
reported_scents:
  jz %7 reported_sounds
  ld %0 t_hear
  call %a print
  ld %0 t_bats
  call %a print
  .line
reported_sounds:
  .input %0
  st [player] %0
  and %0 0xF
  jmp game_loop
taken_by_bats:
  ld %0 t_bats
  call %a print
  .rand %0
  and %0 0xF
  st [player] %0
  jmp game_loop
eaten:
  ld %0 t_wumpus
  call %a print
  jmp game_over
win:
  ld %0 t_amulet
  call %a print
game_over:
  .line
  halt