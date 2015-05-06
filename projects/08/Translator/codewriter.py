from consts import VmConsts
import os


class VmCodeWriter(object):
    ''' Translates VM commands into Hack assembly code.
    '''
    toStackHead = '@SP\nA = M\n'
    toStackTop = toStackHead + 'A = A - 1\n'
    popStackToD = '@SP\nM = M - 1\nA = M\nD = M\n'

    pushDToStack = toStackHead + 'M = D\n@SP\nM = M + 1\n'

    def __init__(self, outFile):
        ''' Opens the output file and gets ready to write into it.
        '''
        print 'Output file name: {0}'.format(os.path.abspath(outFile))
        self.outFile = open(outFile, 'wt')
        self.count = 0
        self._curFileName = ''
        self._curFunctionName = ''

    def setFileName(self, fileName):
        ''' Informs the code writer that the translation of a new VM file has started.
        '''
        self._curFileName = fileName

    def setFunctionName(self, funcName):
        ''' Informs the code writer that the translation of a new function has started.
        '''
        self._curFunctionName = funcName

    def writeArithmetic(self, command):
        ''' Writes the assembly code that is the translation of the given arithmetic command.
        '''
        ops = {'add': 'M = M + D',
               'sub': 'M = M - D',
               'neg': 'M = -M',
               'eq': 'D = M - D\nM = -1\n@LBL{0}\nD;JEQ\n{1}M = M + 1\n(LBL{0})'.format(self.count, self.toStackTop),
               'gt': 'D = M - D\nM = -1\n@LBL{0}\nD;JGT\n{1}M = M + 1\n(LBL{0})'.format(self.count, self.toStackTop),
               'lt': 'D = M - D\nM = -1\n@LBL{0}\nD;JLT\n{1}M = M + 1\n(LBL{0})'.format(self.count, self.toStackTop),
               'and': 'M = M & D',
               'or': 'M = M | D',
               'not': 'M = !M'
               }

        hackCode = ''

        # Pop stack and store in D for two-variable operations
        if command not in ['not', 'neg']:
            hackCode = self.popStackToD
            if command in ['eq', 'gt', 'lt']:
                self.count += 1

        hackCode += self.toStackHead + 'A = A - 1\n'
        hackCode += ops[command] + '\n'
        self.outFile.write(hackCode)

    def writePushPop(self, command, segment, index):
        ''' Writes the assembly code that is the translation of the given push/pop command.
        '''
        hackCode = ''
        segmentToHackConstant = {
            'static': '{0}.{1}',
            'local': 'LCL',
            'argument': 'ARG',
            'this': 'THIS',
            'that': 'THAT',
            'pointer': 'THIS',
            'temp': '5',  # Not using TEMP because it maps to 16 instead of 5.
            'constant': ''
        }
        segmentPos = segmentToHackConstant[segment]
        if segment == 'static':
            segmentPos = segmentPos.format(self._curFileName, index)
            index = 0

        if command == VmConsts.C_PUSH:
            loadToD = '@{index}\nD = A\n'
            if segment in ['temp', 'pointer', 'static']:
                loadToD += '@{segmentPos}\nA = A + D\nD = M\n'
            elif segment != 'constant':
                loadToD += '@{segmentPos}\nA = M + D\nD = M\n'

            loadToD = loadToD.format(segmentPos=segmentPos, index=index)
            hackCode = loadToD + self.pushDToStack

        elif command == VmConsts.C_POP:
            loadSegmentToR13 = '@{index}\nD = A\n'
            if segment in ['temp', 'pointer', 'static']:
                loadSegmentToR13 += '@{segmentPos}\nD = A + D\n@R13\nM = D\n'
            else:
                loadSegmentToR13 += '@{segmentPos}\nD = M + D\n@R13\nM = D\n'

            loadSegmentToR13 = loadSegmentToR13.format(segmentPos=segmentPos, index=index)
            loadDToSegment = '@R13\nA = M\nM = D\n'

            hackCode = loadSegmentToR13 + self.popStackToD + loadDToSegment
        self.outFile.write(hackCode)

    def writeInit(self):
        '''Writes the assembly code that effects the VM initialization (also called bootstrap
        code). This code should be placed in the ROM beginning in address 0x0000.'''

        # initialize the stack pointer to 0x0100 and invoke sys.Init
        hackCode = '@256\nD = A\n@SP\nM = D\n'
        self.outFile.write(hackCode)
        self.writeCall('Sys.init', 0)

    def writeLabel(self, label):
        '''Writes the assembly code that is the translation of the given label command'''
        hackCode = '({0})\n'.format(label)
        self.outFile.write(hackCode)

    def writeGoto(self, label):
        '''Writes the assembly code that is the translation of the given goto command. '''
        hackCode = '@{0}\n0;JMP\n'.format(label)
        self.outFile.write(hackCode)

    def writeIf(self, label):
        '''Writes the assembly code that is the translation of the given if-goto command.'''
        hackCode = self.popStackToD
        hackCode += '@{0}\nD;JNE\n'.format(label)
        self.outFile.write(hackCode)

    def writeCall(self, functionName, numArgs):
        '''Writes the assembly code that is the translation of the given Call command.'''

        afterCallLabelName = 'LBL-RETURN-FROM-{0}.{1}.{2}'.format(self._curFileName, self._curFunctionName, self.count)
        self.count += 1

        # Push return address, LCL, ARG, THIS, THAT
        hackCode = '@{afterCallLabelName}\nD=A\n{pushD}'.format(afterCallLabelName=afterCallLabelName,
                                                                pushD=self.pushDToStack)
        hackCode += '@LCL\nD=M\n{pushD}'.format(pushD=self.pushDToStack)
        hackCode += '@ARG\nD=M\n{pushD}'.format(pushD=self.pushDToStack)
        hackCode += '@THIS\nD=M\n{pushD}'.format(pushD=self.pushDToStack)
        hackCode += '@THAT\nD=M\n{pushD}'.format(pushD=self.pushDToStack)

        # Reposition ARG and LCL
        hackCode += '@{n}\nD = A\n@5\nD = D + A\n@SP\nD = M - D\n@ARG\nM = D\n'.format(n=numArgs)
        hackCode += '@SP\nD = M\n@LCL\nM = D\n'

        self.outFile.write(hackCode)

        # Goto function
        self.writeGoto(functionName)

        # Create return label
        hackCode = '({0})\n'.format(afterCallLabelName)
        self.outFile.write(hackCode)

    def writeReturn(self):
        '''Writes the assembly code that is the translation of the given Return command'''

        loadFrameMinusNToLbl = '@{1}\nD = A\n@R13\nA = M - D\nD = M\n@{0}\nM = D\n'
        # Frame (R13) = LCL
        hackCode = '@LCL\nD = M\n@R13\nM = D\n'

        # Store return value in R14
        hackCode += loadFrameMinusNToLbl.format('R14', 5)

        # Restore caller stack
        hackCode += self.popStackToD + '@ARG\nA = M\nM = D\n'
        hackCode += '@ARG\nD = M + 1\n@SP\nM = D\n'
        hackCode += loadFrameMinusNToLbl.format('THAT', 1)
        hackCode += loadFrameMinusNToLbl.format('THIS', 2)
        hackCode += loadFrameMinusNToLbl.format('ARG', 3)
        hackCode += loadFrameMinusNToLbl.format('LCL', 4)
        hackCode += '@R14\nA = M\n0;JMP\n'
        self.outFile.write(hackCode)

    def writeFunction(self, functionName, numLocals):
        '''Writes the assembly code that is the trans. of the given Function command.'''
        self.setFunctionName(functionName)
        hackCode = '({0})\nD = 0\n'.format(functionName)
        hackCode += (self.pushDToStack * numLocals)
        self.outFile.write(hackCode)

    def close(self):
        ''' Closes the output file.
        '''
        self.outFile.write('(END)\n@END\n0;JMP\n')
        self.outFile.close()
