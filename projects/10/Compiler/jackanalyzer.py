import os
import sys
from sys import argv
import traceback

from consts import AnalyzerConsts
from jacktokenizer import JackTokenizer
from compilationengine import CompilationEngine

XML_SYMBOL_REPLACE = { '<': '&lt;', '>': '&gt;', '&': '&amp;' }
XML_ELEMENT = '<{0}> {1} </{0}>\n'

class JackAnalyzer:
    def __init__(self, source):
        self.jackFilesToCompile = []
        if os.path.isdir(source):
            filesInSourceDir = [os.path.join(source,f) for f in os.listdir(source) if f.endswith('.jack')]
            self.jackFilesToCompile.extend(filesInSourceDir)
        elif os.path.isfile(source):
            self.jackFilesToCompile.append(source)
        else:
            print 'Invalid input source: {0}'.format(source)
            exit(1);

    def getListOfXmlTokens(self, jackFilePath):
        tokenizer = JackTokenizer(jackFilePath)
        outList = ['<tokens>\n']
        while tokenizer.hasMoreTokens():
            tokenizer.advance()
            tokenType = tokenizer.tokenType()
            if tokenType == AnalyzerConsts.KEYWORD:
                outList.append(XML_ELEMENT.format('keyword', tokenizer.keyWord().lower()))
            elif tokenType == AnalyzerConsts.SYMBOL:
                symbol = tokenizer.symbol()
                outList.append(XML_ELEMENT.format('symbol', XML_SYMBOL_REPLACE.get(symbol,symbol)))
            elif tokenType == AnalyzerConsts.IDENTIFIER:
                outList.append(XML_ELEMENT.format('identifier', tokenizer.identifier()))
            elif tokenType == AnalyzerConsts.INT_CONST:
                outList.append(XML_ELEMENT.format('integerConstant', tokenizer.intVal()))
            elif tokenType == AnalyzerConsts.STRING_CONST:
                outList.append(XML_ELEMENT.format('stringConstant', tokenizer.stringVal()))
        outList.append('</tokens>\n')
        return outList

    def analyze(self):
        for jackFilePath in self.jackFilesToCompile:
            listOfXmlTokens = self.getListOfXmlTokens(jackFilePath)
            outFile = open(jackFilePath.replace('.jack', 'T.xml'), 'wt')
            outFile.writelines(listOfXmlTokens)
            outFile = open(jackFilePath.replace('.jack', '.xml'), 'wt')
            compileEngine = CompilationEngine(listOfXmlTokens, outFile)
            compileEngine.compileClass()
            outFile.close()

if __name__ == "__main__":
    if len(argv) != 2:
        print "Compile a JACK program to .xml files \
                \nUsage: \
                \n\t{0}\t<file.jack | directory>".format(argv[0])
        exit(1)
    analyzer = JackAnalyzer(argv[1])
    try:
        analyzer.analyze()
        print "Done."
    except Exception, e:
        print 'Compilation Failed: {0}'.format(e)
        traceback.print_exc()
