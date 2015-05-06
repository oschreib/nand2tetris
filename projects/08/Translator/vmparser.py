import re

from consts import VmConsts


class VmParser(object):
    ''' Parser for parsing hack-asm lines to hack instructions'''

    keywordToCmdType = {'add': VmConsts.C_ARITHMETIC,
                        'sub': VmConsts.C_ARITHMETIC,
                        'neg': VmConsts.C_ARITHMETIC,
                        'eq': VmConsts.C_ARITHMETIC,
                        'gt': VmConsts.C_ARITHMETIC,
                        'lt': VmConsts.C_ARITHMETIC,
                        'and': VmConsts.C_ARITHMETIC,
                        'or': VmConsts.C_ARITHMETIC,
                        'not': VmConsts.C_ARITHMETIC,
                        'push': VmConsts.C_PUSH,
                        'pop': VmConsts.C_POP,
                        'label': VmConsts.C_LABEL,
                        'goto': VmConsts.C_GOTO,
                        'if-goto': VmConsts.C_IF,
                        'function': VmConsts.C_FUNCTION,
                        'return': VmConsts.C_RETURN,
                        'call': VmConsts.C_CALL
                        }


    def __init__(self, codeLines):
        '''Initialize the parser with a list of the lines of code'''
        self.code = filter(lambda l: len(l) > 0, map(lambda l: re.sub('//.*', '', l).strip(), codeLines))
        self.it = -1

    def hasMoreCommands(self):
        '''Returns true iff there are more commands in the input'''
        return self.it + 1 < len(self.code)

    def advance(self):
        '''Reads the next command from the input and makes it the current command. Should be called only
            if hasMoreCommands() is true. Initially there is no current command.
        '''
        # Find the next line of code
        self.it += 1
        self.curCommand = self.code[self.it]
        self.parseCommand(self.curCommand)

    def parseCommand(self, command):
        '''Parses the command into arguments.
        '''
        self.splitCmd = command.split(' ')

    def commandType(self):
        '''Returns the type of the current command.
        '''
        return self.keywordToCmdType[self.splitCmd[0]]

    def getSplitCommand(self):
        return self.splitCmd
