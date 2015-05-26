class VMWriter:
    SEGMENT_COMPILE = {
        'CONST': 'constant',
        'ARG': 'argument',
        'STATIC': 'static',
        'LOCAL': 'local',
        'THIS': 'this',
        'THAT': 'that',
        'POINTER': 'pointer',
        'TEMP': 'temp',
    }
    def __init__(self, outputFile):
        self.out = open(outputFile, 'wt')

    def writePush(self, segment, index):
        """ Writes a VM push command """
        self.out.write('push {0} {1}\n'.format(self.SEGMENT_COMPILE[segment], index))

    def writePop(self, segment, index):
        """ Writes a VM pop command """
        self.out.write('pop {0} {1}\n'.format(self.SEGMENT_COMPILE[segment], index))

    def writeArithmetic(self, command):
        """ Writes a VM arithmetic command """
        self.out.write(command.lower() + '\n')

    def writeLabel(self, label):
        """ Writes a VM label command """
        self.out.write('label {0}\n'.format(label))

    def writeGoto(self, label):
        """ Writes a VM goto command """
        self.out.write('goto {0}\n'.format(label))

    def writeIf(self, label):
        """ Writes a VM if-goto command"""
        self.out.write('if-goto {0}\n'.format(label))

    def writeCall(self, name, numOfArgs):
        """" Writes a VM call command """
        self.out.write('call {0} {1}\n'.format(name, numOfArgs))

    def writeFunction(self, name, numOfLocals):
        """ Writes a VM function command """
        self.out.write('function {0} {1}\n'.format(name, numOfLocals))

    def writeReturn(self):
        """" Writes a VM return command """
        self.out.write('return\n')

    def close(self):
        """ Closes the output file """
        self.out.close()

