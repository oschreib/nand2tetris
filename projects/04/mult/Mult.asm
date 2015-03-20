// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Add R0+R0... R1 times.
  @R2
  M=0 // R2 = 0
  @R1
  D=M // D = R1
  @R4
  M=D // Store a copy of R1 in R4 so we don't change R1

(LOOP)
  @R4
  D=M // D = R4
  @END
  D;JEQ // If R4 == 0 goto END
  @R0
  D=M // D = R0
  @R2
  M=D+M // R2 += R0
  @R4
  M=M-1 // R4--
  @LOOP
  0;JMP // Goto LOOP

(END)
  @END
  0;JMP // Infinite loop
