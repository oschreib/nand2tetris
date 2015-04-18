
import re
import hackcode

class HackParser(object):
    ''' Parser for parsing hack-asm lines to hack instructions'''
    A_COMMAND = 0
    C_COMMAND = 1
    L_COMMAND = 2

    def __init__(self, codeLines):
        '''Initialize the parser with a list of the lines of code'''
        self.code = filter(lambda l: len(l) > 0, map(lambda l: re.sub('//.*', '', l).strip(), codeLines))

        self.it = -1
        self.lineInCode = 0

    def hasMoreCommands(self):
        '''Returns true iff there are more commands in the input'''
        return self.it  + 1 < len(self.code)

    def advance(self):
        '''Reads the next command from the input and makes it the current command. Should be called only
            if hasMoreCommands() is true. Initially there is no current command.
        '''
        # Find the next line of code (ignore comments and empty lines)
        self.it += 1
        self.curCommand = self.code[self.it]
        self.parseCommand(self.curCommand)

        # Count lines of code
        if self.curCommandType != self.L_COMMAND:
            self.lineInCode += 1

    def getLineInCode(self):
        return self.lineInCode

    def parseCommand(self, command):
        self.alCmdSymbol = ''
        self.cCmdDest = ''
        self.cCmdComp = ''
        self.cCmdJump = ''

        if command.startswith('@'):
            self.curCommandType = self.A_COMMAND
            self.alCmdSymbol = command[1:]
        elif command.startswith('(') and command.endswith(')'):
            self.curCommandType =  self.L_COMMAND
            self.alCmdSymbol = command[1:-1]
        else:
            self.curCommandType =  self.C_COMMAND

            # Parse the various parts of the C TYPE instruction
            eqPos = command.find('=')
            if eqPos > 0:
                self.cCmdDest = command[:eqPos]
                command = command[eqPos + 1:]
            else:
                self.cCmdDest = ''

            semicolonPos = command.find(';')
            if semicolonPos > 0:
                self.cCmdJump  = command[semicolonPos + 1:]
                command = command[: semicolonPos]
            else:
                self.cCmdJump = ''

            self.cCmdComp = command

    def commandType(self):
        '''Returns the type of the current command:
                * A_COMMAND for @Xxx where Xxx is either a symbol or a decimal number
                * C_COMMAND for dest=comp;jump
                * L_COMMAND (actually, pseudocommand) for (Xxx) where Xxx is a symbol.
        '''
        return self.curCommandType

    def symbol(self):
        ''' Returns the symbol or decimal Xxx of the current command @Xxx or (Xxx). Should be called
            only when commandType() is A_COMMAND or L_COMMAND.
        '''

        if self.curCommandType == self.C_COMMAND:
            raise Exception("Invalid command type for symbol at line: {0}".format(self.curCommand))

        return self.alCmdSymbol

    def dest(self):
        '''Returns the dest mnemonic in the current C-command (8 possibilities).
            Should be called only when commandType() is C_COMMAND.
        '''
        if self.curCommandType != self.C_COMMAND:
            raise Exception("Invalid command type for dest at line: {0}".format(self.curCommand))

        return self.cCmdDest


    def comp(self):
        '''Returns the comp mnemonic in the current C-command (28 possibilities).
            Should be called only when commandType() is C_COMMAND.
        '''
        if self.curCommandType != self.C_COMMAND:
            raise Exception("Invalid command type for comp at line: {0}".format(self.curCommand))

        return self.cCmdComp

    def jump(self):
        '''Returns the jump mnemonic in the current C-command (8 possibilities).
            Should be called only when commandType() is C_COMMAND.
        '''
        if self.curCommandType != self.C_COMMAND:
            raise Exception("Invalid command type for jump at line: {0}".format(self.curCommand))

        return self.cCmdJump
