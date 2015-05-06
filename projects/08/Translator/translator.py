import os
import sys
from sys import argv
import traceback

from consts import VmConsts
from vmparser import VmParser
from codewriter import VmCodeWriter


def translate(fileName):
    files = []
    outFile = ''
    if os.path.isdir(fileName):
        # Get all file names in dir
        files = [os.path.join(fileName,f) for f in os.listdir(fileName) if f.endswith('.vm')]
        outFile = os.path.join(fileName, fileName[fileName.rfind(os.sep) + 1:] + '.asm')
    else:
        # Single file
        files.append(fileName)
        outFile = fileName.replace('.vm', '.asm')

    codeWriter = VmCodeWriter(outFile)
    codeWriter.writeInit()

    for f in files:
        codeLines = open(f, 'rt').readlines()
        parser = VmParser(codeLines)
        codeWriter.setFileName(os.path.basename(f))

        # Compile the byte code
        while parser.hasMoreCommands():
            parser.advance()
            cmdType = parser.commandType()
            cmdSplit = parser.getSplitCommand()
            if cmdType == VmConsts.C_PUSH or cmdType == VmConsts.C_POP:
                codeWriter.writePushPop(cmdType, cmdSplit[1], int(cmdSplit[2]))
            elif cmdType == VmConsts.C_ARITHMETIC:
                codeWriter.writeArithmetic(cmdSplit[0])
            elif cmdType == VmConsts.C_LABEL:
                codeWriter.writeLabel(cmdSplit[1])
            elif cmdType == VmConsts.C_GOTO:
                codeWriter.writeGoto(cmdSplit[1])
            elif cmdType == VmConsts.C_IF:
                codeWriter.writeIf(cmdSplit[1])
            elif cmdType == VmConsts.C_FUNCTION:
                codeWriter.writeFunction(cmdSplit[1], int(cmdSplit[2]))
            elif cmdType == VmConsts.C_RETURN:
                codeWriter.writeReturn()
            elif cmdType == VmConsts.C_CALL:
                codeWriter.writeCall(cmdSplit[1], int(cmdSplit[2]))
            else:
                print 'UNKONWN COMMAND TYPE! {0}'.format(cmdType)

    codeWriter.close()


if __name__ == "__main__":
    if len(argv) != 2:
        print "Translate a VM program to the HACK assembly language \
                \nUsage: \
                \n\t{0}\t<file.vm | directory>".format(argv[0])
        exit(1)
    elif not os.path.isdir(argv[1]) and not argv[1].endswith('.vm'):
        print "Error! File must end with .vm"
        exit(1)
    try:
        translate(argv[1])
        print "Done."
    except Exception, e:
        print 'Compilation Failed: {0}'.format(e)
        traceback.print_exc()
