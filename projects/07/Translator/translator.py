

import os
import sys
from sys import argv
import traceback

from consts import VmConsts
from vmparser import VmParser
from codewriter import VmCodeWriter


def translate(fileName):
    codeLines = open(fileName, 'rt').readlines()
    parser = VmParser(codeLines)
    codeWriter = VmCodeWriter(fileName.replace('.vm','.asm')) # TODO: if directory, find other filename


    # Compile the byte code
    while parser.hasMoreCommands():
        parser.advance()
        cmdType = parser.commandType()
        cmdSplit = parser.getSplitCommand()
        if cmdType == VmConsts.C_PUSH or cmdType == VmConsts.C_POP:
            # PUSH / POP command
            codeWriter.writePushPop(cmdType, cmdSplit[1], int(cmdSplit[2]))
        elif cmdType == VmConsts.C_ARITHMETIC:
            # ARITHMETIC commands
            codeWriter.writeArithmetic(cmdSplit[0])

    codeWriter.close()

if __name__ == "__main__":
    if len(argv) != 2:
        print "Translate a VM program to the HACK assembly language \
                \nUsage: \
                \n\t{0}\t<file.vm | directory>".format(argv[0])
        exit(1)
    elif not argv[1].endswith('.vm'):
        print "Error! File must end with .vm"
        exit(1)
        # TODO: HANDLE DIRECTORIES
    try:
        translate(argv[1])
        print "Done."
    except Exception, e:
        print 'Compilation Failed: {0}'.format(e)
