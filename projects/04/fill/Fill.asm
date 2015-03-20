// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, the
// program clears the screen, i.e. writes "white" in every pixel.

(LOOP)
  @col
  M = 0 // Set pixel color to WHITE
  @KBD
  D = M
  @WHITE
  D;JEQ // If D==0 then goto WHITE, else col=BLACK
  @col
  M = M - 1 // Set pixel color to BLACK (-1)

(WHITE)
  @8192 // Size of screen (256  * (512 / 16))
  D = A
  @i
  M = D // i = 8192
  @SCREEN
  D = A
  @pos
  M = D // pos = SCREEN

// Paint entire screen
(PAINTLOOP)
  @col
  D = M // D = col (WHITE / BLACK)

  @pos
  A = M // A = pos
  M = D // paint pixel the required color
  @pos
  M = M + 1 // Move to next pixel on screen
  @i
  M = M - 1 // i--
  D = M // D = i
  @PAINTLOOP
  D;JGT // While (i > 0) Goto PAINTLOOP

  @LOOP
  0;JMP // Goto LOOP

(END)
  @END
  0;JMP // Infinite loop
