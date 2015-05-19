
import re
from consts import AnalyzerConsts

# Matches one-line and multi-line comments
COMMENTS_REGEX = '(//.*?\n)|(/\*.*?\*/)'


KEYWORD_REGEX       = 'class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|' + \
                      'this|let|do|if|else|while|return'
SYMBOL_REGEX        = '[{}()[\].,;+\-*/&|<>=~]'
INTEGER_REGEX       = '\d+'
STRING_REGEX        = '[^\n\"]*'
IDENTIFIER_REGEX    = '[A-Za-z_][A-Za-z_0-9]*'

TOKEN_REGEX = '({0})|({1})|({2})|\"({3})\"|({4})'.format(KEYWORD_REGEX, SYMBOL_REGEX, INTEGER_REGEX, STRING_REGEX,
                IDENTIFIER_REGEX)

KEYWORD_POS = 0
SYMBOL_POS = 1
INTEGER_POS = 2
STRING_POS = 3
IDENTIFIER_POS = 4

class JackTokenizer:
    def __init__(self, path):
        '''Opens the input file/stream and gets ready to tokenize it'''
        fileContents = open(path, 'rt').read()
        noComments = re.sub(COMMENTS_REGEX, '', fileContents, flags = re.S)
        self.tokens = re.findall(TOKEN_REGEX, noComments)
        self.tokens.insert(0, 'DUMMY')

    def hasMoreTokens(self):
        ''' Returns true iff there are more tokens to read'''
        return len(self.tokens) > 1

    def advance(self):
        '''gets the next token from the input and makes it the current token.'''
        self.tokens.pop(0)

    def tokenType(self):
        '''returns the type of the current token'''
        if self.tokens[0][KEYWORD_POS] != '':    return AnalyzerConsts.KEYWORD
        if self.tokens[0][SYMBOL_POS] != '':     return AnalyzerConsts.SYMBOL
        if self.tokens[0][IDENTIFIER_POS] != '': return AnalyzerConsts.IDENTIFIER
        if self.tokens[0][INTEGER_POS] != '':    return AnalyzerConsts.INT_CONST
        if self.tokens[0][STRING_POS] != '':     return AnalyzerConsts.STRING_CONST
        return -1

    def keyWord(self):
        '''returns the keyword which is the current token'''
        return self.tokens[0][KEYWORD_POS].upper()

    def symbol(self):
        '''returns the character which is the current token'''
        return self.tokens[0][SYMBOL_POS]

    def identifier(self):
        '''returns the identifier which is the current token'''
        return self.tokens[0][IDENTIFIER_POS]

    def intVal(self):
        '''returns the integer value of the current token'''
        return int(self.tokens[0][INTEGER_POS])

    def stringVal(self):
        '''returns the string value of the current token'''
        return self.tokens[0][STRING_POS]
