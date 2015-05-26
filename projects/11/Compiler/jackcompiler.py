import os
from sys import argv
import traceback

from consts import CompilerConsts
from jacktokenizer import JackTokenizer
from compilationengine import CompilationEngine
from vmwriter import VMWriter

XML_ELEMENT = '<{0}> {1} </{0}>\n'

class JackCompiler:
    def __init__(self, source):
        self.jackFilesToCompile = []
        if os.path.isdir(source):
            filesInSourceDir = [os.path.join(source,f) for f in os.listdir(source) if f.endswith('.jack')]
            self.jackFilesToCompile.extend(filesInSourceDir)
        elif os.path.isfile(source):
            self.jackFilesToCompile.append(source)
        else:
            print 'Invalid input source: {0}'.format(source)
            exit(1)

    def getListOfXmlTokens(self, jackFilePath):
        tokenizer = JackTokenizer(jackFilePath)
        outList = ['<tokens>\n']
        while tokenizer.hasMoreTokens():
            tokenizer.advance()
            tokenType = tokenizer.tokenType()
            if tokenType == CompilerConsts.KEYWORD:
                outList.append(XML_ELEMENT.format('keyword', tokenizer.keyWord().lower()))
            elif tokenType == CompilerConsts.SYMBOL:
                symbol = tokenizer.symbol()
                outList.append(XML_ELEMENT.format('symbol', symbol))
            elif tokenType == CompilerConsts.IDENTIFIER:
                outList.append(XML_ELEMENT.format('identifier', tokenizer.identifier()))
            elif tokenType == CompilerConsts.INT_CONST:
                outList.append(XML_ELEMENT.format('integerConstant', tokenizer.intVal()))
            elif tokenType == CompilerConsts.STRING_CONST:
                outList.append(XML_ELEMENT.format('stringConstant', tokenizer.stringVal()))
        outList.append('</tokens>\n')
        return outList

    def compile(self):
        for jackFilePath in self.jackFilesToCompile:
            listOfXmlTokens = self.getListOfXmlTokens(jackFilePath)
            compileEngine = CompilationEngine(listOfXmlTokens[1:-1], VMWriter(jackFilePath.replace('.jack', '.vm')))
            compileEngine.compileClass()

if __name__ == "__main__":
    if len(argv) != 2:
        print "Compile a JACK program to .xml files \
                \nUsage: \
                \n\t{0}\t<file.jack | directory>".format(argv[0])
        exit(1)
    compiler = JackCompiler(argv[1])
    try:
        compiler.compile()
        print "Done."
    except Exception, e:
        print 'Compilation Failed: {0}'.format(e)
        traceback.print_exc()
