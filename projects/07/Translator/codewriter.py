from consts import VmConsts

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
        self.outFile = open(outFile, 'wt')
        self.count = 0

    def setFileName(self, fileName):
        ''' Informs the code writer that the translation of a new VM file has started.
        '''
        self.curFileName = fileName

    def writeArithmetic(self, command):
        ''' Writes the assembly code that is the translation of the given arithmetic command.
        '''
        ops = { 'add': 'M = M + D',
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
            'static': '16',
            'local': 'LCL',
            'argument': 'ARG',
            'this': 'THIS',
            'that': 'THAT',
            'pointer': 'THIS', #TODO: CHECK
            'temp': '5', # TODO: Not using TEMP because it maps to 16 instead of 5.
            'constant': ''
        }
        segmentPos = segmentToHackConstant[segment]

        if command == VmConsts.C_PUSH:
            loadToD = '@{index}\nD = A\n'
            if segment in ['temp', 'pointer']:
                loadToD += '@{segmentPos}\nA = A + D\nD = M\n'
            elif segment != 'constant':
                loadToD += '@{segmentPos}\nA = M + D\nD = M\n'

            loadToD = loadToD.format(segmentPos=segmentPos, index=index)
            hackCode = loadToD + self.pushDToStack

        elif command == VmConsts.C_POP:
            loadSegmentToR13 = '@{index}\nD = A\n'
            if segment in ['temp', 'pointer']:
                loadSegmentToR13 += '@{segmentPos}\nD = A + D\n@R13\nM = D\n'
            else:
                loadSegmentToR13 += '@{segmentPos}\nD = M + D\n@R13\nM = D\n'

            loadSegmentToR13 = loadSegmentToR13.format(segmentPos=segmentPos, index=index)
            loadDToSegment = '@R13\nA = M\nM = D\n'

            hackCode = loadSegmentToR13 + self.popStackToD + loadDToSegment
        self.outFile.write(hackCode)

    def close(self):
        ''' Closes the output file.
        '''
        self.outFile.write('(END)\n@END\n0;JMP\n')
        self.outFile.close()
