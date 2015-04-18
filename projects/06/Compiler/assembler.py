

import os
import sys
from sys import argv
import traceback

from hackparser import HackParser
from hackcode import HackCode
from symboltable import SymbolTable

def assemble(fileName):
    symbolTable = SymbolTable()
    codeLines = open(fileName, 'rt').readlines()
    parser = HackParser(codeLines)

    # First pass - get the labels
    while parser.hasMoreCommands():
        l = ''
        parser.advance()
        cmdType = parser.commandType()
        if cmdType == HackParser.L_COMMAND:
            # L COMMAND
            #add entry to symbolTable
            symbolTable.addEntry(parser.symbol(), parser.getLineInCode())

    parser = HackParser(codeLines)
    outLines = []

    # Second pass - compile the code
    while parser.hasMoreCommands():
        parser.advance()
        cmdType = parser.commandType()
        if cmdType == HackParser.A_COMMAND:
            # A COMMAND
            #if symbol is number - A = symbol, else get entry from symbolTable
            symbol = parser.symbol()
            if symbol.isdigit():
                l = '0{:015b}'.format(int(symbol))
            else:
                l = '0{:015b}'.format(symbolTable.getAddress(symbol))
            outLines.append(l)
        elif cmdType == HackParser.C_COMMAND:
            # C COMMAND
            dest = HackCode.dest(parser.dest())
            comp = HackCode.comp(parser.comp())
            jump  = HackCode.jump(parser.jump())
            l = '111' + comp + dest + jump
            outLines.append(l)

    outLines.append('') # Add an empty line
    open(argv[1][:-3] + 'hack', 'wt').write('\n'.join(outLines))

if __name__ == "__main__":
    if len(argv) != 2:
        print "Assemble a program written int he HACK assembly language \
                \nUsage: \
                \n\t{0}\t<file.asm>".format(argv[0])
        exit(1)
    elif not argv[1].endswith('.asm'):
        print "Error! File must end with .asm"
        exit(1)
    try:
        assemble(argv[1])
    except Exception, e:
        print 'Compilation Failed: {0}'.format(e)
