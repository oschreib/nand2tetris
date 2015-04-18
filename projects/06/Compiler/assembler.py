

import os
import sys
from sys import argv

from hackparser import HackParser

class SymbolTable(object):
    def __init__(self):
        self.d = dict()
        self.counter = 0

    def addEntry(symbol):
        address = self.counter #TODO: should be *2 (in bytes?)
        self.d[symbol] = address
        self.counter += 1
        return address

    def addEntry(symbol, address):
        self.d[symbol] = address

    def contains(self, symbol):
        return symbol in self.d

    def getAddress(symbol):
        if self.contains():
            return self.d[symbol]
        return addEntry(symbol)


if __name__ == "__main__":
    if not argv[1].endswith('.asm'):
        print "Error! File must end with .asm"
        exit(1)
    try:
        symbolTable = SymbolTable()
        codeLines = open(argv[1], 'rt').readlines()
        parser = HackParser(codeLines)
        outLines = []
        while parser.hasMoreCommands():
            parser.advance()
            cmdType = parser.commandType()
            if cmdType == HackParser.A_COMMAND:
                # A COMMAND
                #if symbol is number - A = symbol, else get entry from symbolTable
                symbol = parser.symbol()

            elif cmdType == HackParser.L_COMMAND:
                # L COMMAND
                #add entry to symbolTable
                symbolTablesymbol = parser.symbol()
            elif cmdType == HackParser.C_COMMAND:
                # C COMMAND
                dest = HackCode.dest(parser.dest())
                comp = HackCode.comp(parser.comp())
                jump  = HackCode.jump(parser.jump())



        open(argv[1][:-3] + 'hack', 'wt').writelines(outLines)
    except Exception, e:
        print 'Error: {0}'.format(e)
