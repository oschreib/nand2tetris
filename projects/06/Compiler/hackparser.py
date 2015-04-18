
from hackcode import HackCode

class HackParser(object):
    A_COMMAND = 0
    C_COMMAND = 1
    L_COMMAND = 2

    def __init__(self, codeLines):
        '''Initialize the parser with a list of the lines of code'''
        self.code = codeLines

    def hasMoreCommands(self):
        '''Returns true iff there are more commands in the input'''

    def advance(self):
        '''Reads the next command from the input and makes it the current command. Should be called only
            if hasMoreCommands() is true. Initially there is no current command.
        '''

    def commandType(self):
        '''Returns the type of the current command:
                * A_COMMAND for @Xxx where Xxx is either a symbol or a decimal number
                * C_COMMAND for dest=comp;jump
                * L_COMMAND (actually, pseudocommand) for (Xxx) where Xxx is a symbol.
        '''

    def symbol(self):
        ''' Returns the symbol or decimal Xxx of the current command @Xxx or (Xxx). Should be called
            only when commandType() is A_COMMAND or L_COMMAND.
        '''
    def dest(self):
        '''Returns the dest mnemonic in the current C-command (8 possibilities).
            Should be called only when commandType() is C_COMMAND.
        '''

    def comp(self):
        '''Returns the comp mnemonic in the current C-command (28 possibilities).
            Should be called only when commandType() is C_COMMAND.
        '''

    def jump(self):
         '''Returns the jump mnemonic in the current C-command (8 possibilities).
            Should be called only when commandType() is C_COMMAND.
        '''
