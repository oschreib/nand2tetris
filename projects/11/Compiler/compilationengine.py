import re

from symboltable import SymbolTable
from consts import CompilerConsts

class CompilationEngine:
    """This module effects the actual compilation into XML form.
    It gets its input from a JackTokenizer and writes its parsed VM-code into an output file/stream.
    This is done by a series of compilexxx() methods, where xxx is a corresponding syntactic element of the
    Jack grammar. The contract between these methods is that each compilexxx() method should read the
    syntactic construct xxx from the input, advance() the tokenizer exactly beyond xxx, and output the VM code
    parsing of xxx. Thus, compilexxx() may only be called if indeed xxx is the next syntactic element of
    the input."""

    STATEMENT_REGEX = '(let)|(if)|(while)|(do)|(return)'
    OP_REGEX = r'> (\+|-|\*|/|&|\||<|>|=) <'
    UNARY_OP_REGEX = r'> (-|~) <'

    CALL_KIND_COMPILE = {
        'ARG': 'ARG',
        'STATIC': 'STATIC',
        'VAR': 'LOCAL',
        'FIELD': 'THIS'
    }

    ARITHMETIC_COMPILE = {
        '+': 'ADD',
        '-': 'SUB',
        '=': 'EQ',
        '>': 'GT',
        '<': 'LT',
        '&': 'AND',
        '|': 'OR'
    }

    ARITHMETIC_UNARY_COMPILE = {
        '-': 'NEG',
        '~': 'NOT'
    }

    ARITHMETIC_BUILTIN_FUNCS = {
        '*': 'Math.multiply',
        '/': 'Math.divide'
    }

    def __init__(self, inputXmlTokens, vmwriter):
        self.input = inputXmlTokens
        self.vmWriter = vmwriter
        self.symbolTable = SymbolTable()
        self.className = ''
        self.labelIndex = 0

    def pop(self):
        p = self.top()
        self.input.pop(0)
        return p

    def top(self):
        return self.input[0]

    def stripTop(self):
        x = self.top()
        x = x[x.index('>') + 2: x.rindex('<')-1]
        return x

    def stripPop(self):
        x = self.stripTop()
        self.pop()
        return x

    def topType(self):
        t = self.top()
        if '<keyword>' in t:
            return CompilerConsts.KEYWORD
        elif '<symbol>' in t:
            return CompilerConsts.SYMBOL
        elif '<symbol>' in t:
            return CompilerConsts.SYMBOL
        elif '<identifier>' in t:
            return CompilerConsts.IDENTIFIER
        elif '<integerConstant>' in t:
            return CompilerConsts.INT_CONST
        elif '<stringConstant>' in t:
            return CompilerConsts.STRING_CONST

    def compileClass(self):
        """compiles a complete class."""
        self.pop()  # class keyword
        self.className = self.stripPop()  # class name
        self.pop()  # {

        # Write class fields
        while re.search('static|field', self.top()):
            self.compileClassVarDec()

        # Write class methods
        while re.search('constructor|function|method', self.top()):
            self.compileSubroutine()

        self.vmWriter.close()

    def compileClassVarDec(self):
        """compiles a static declaration or a field declaration."""
        kind = self.stripPop()  # var keyword (static / field)
        varType = self.stripPop()  # type
        varName = self.stripPop()  # variable name
        self.symbolTable.define(varName, varType, kind.upper())

        # Compile additional comma-separated variables
        while re.search(' , ', self.top()):
            self.pop()  # ,
            varName = self.stripPop()  # variable name
            self.symbolTable.define(varName, varType, kind.upper())

        self.pop()  # ;

    def compileSubroutine(self):
        """compiles a complete method, function, or constructor."""
        subroutineKind = self.stripPop()  # subroutine keyword
        self.pop()  # type
        subroutineName = self.stripPop()  # subroutine name
        subroutineFullName = '{0}.{1}'.format(self.className, subroutineName)
        self.symbolTable.startSubroutine()
        print "=="*20
        print self.symbolTable.varCount('ARG')
        print self.symbolTable.varCount('VAR')
        print subroutineFullName
        print "=="*20

        if subroutineKind == 'method':
            self.symbolTable.define('selfClass', self.className, 'ARG')

        self.pop()  # (
        self.compileParameterList()
        self.pop()  # )

        self.pop()  # {

        # Compile all subroutine variables
        while re.search(' var ', self.top()):
            self.compileVarDec()  # subroutine variable declarations

        subroutineLocalsCount = self.symbolTable.varCount('VAR')
        print subroutineLocalsCount
        self.vmWriter.writeFunction(subroutineFullName, subroutineLocalsCount)

        if subroutineKind == 'constructor':
            # Allocate space for class and fields
            fieldsCount = self.symbolTable.varCount('FIELD')
            self.vmWriter.writePush('CONST', fieldsCount)
            self.vmWriter.writeCall('Memory.alloc', 1)
            # Set THIS to allocated memory
            self.vmWriter.writePop('POINTER', 0)

        elif subroutineKind == 'method':
            self.vmWriter.writePush('ARG', 0)
            # Set THIS to first argument
            self.vmWriter.writePop('POINTER', 0)

        self.compileStatements()  # subroutine body statements
        self.pop()  # }

    def compileParameterList(self):
        """compiles a (possibly empty) parameter list, not including the enclosing ()."""
        if not re.search(' \) ', self.top()):
            paramType = self.stripPop()  # var type
            paramName = self.stripPop()  # var name
            self.symbolTable.define(paramName, paramType, 'ARG')

            while re.search(' , ', self.top()):
                self.pop()  # ,
                paramType = self.stripPop()  # var type
                paramName = self.stripPop()  # var name
                self.symbolTable.define(paramName, paramType, 'ARG')

    def compileVarDec(self):
        """compiles a var declaration."""
        self.pop()  # var
        varType = self.stripPop()  # type
        varName = self.stripPop()  # var name
        self.symbolTable.define(varName, varType, 'VAR')

        # Compile additional variables of same type
        while re.search(' , ', self.top()):
            self.pop()  # ,
            varName = self.stripPop()  # var name
            self.symbolTable.define(varName, varType, 'VAR')

        self.pop()  # ;

    def compileStatements(self):
        """compiles a sequence of statements, not including the enclosing {}."""
        # Compile all consecutive statements
        while re.search(self.STATEMENT_REGEX, self.top()):
            group = re.search(self.STATEMENT_REGEX, self.top()).group()
            print "*"*10
            print group
            if group == 'let':
                self.compileLet()
            elif group == 'if':
                self.compileIf()
            elif group == 'while':
                self.compileWhile()
            elif group == 'do':
                self.compileDo()
            elif group == 'return':
                self.compileReturn()
            else:
                print 'Unknown group {0}'.format(group)

    def compileDoCall(self, callName=''):
        if callName == '':
            callName = self.stripPop()  # subroutine call / variable/class name
        fullFunctionName = callName
        argsCount = 0

        # Handle sub-variables / class calls
        if re.search(' \. ', self.top()):
            self.pop()  # .
            print "*"*100
            print self.top()
            subroutineName = self.stripPop()  # subroutine call
            print "*"*100
            print subroutineName

            callKind, callType, callIndex = self.symbolTable.get(callName)
            if callType == 'NOT_FOUND':
                # Calling a static class method
                fullFunctionName = '{0}.{1}'.format(callName, subroutineName)
            else:
                # calling an instance
                self.vmWriter.writePush(self.CALL_KIND_COMPILE[callKind], callIndex)
                fullFunctionName = '{0}.{1}'.format(callType, subroutineName)
                argsCount += 1
        elif re.search(' \( ', self.top()):
            fullFunctionName = '{0}.{1}'.format(self.className, callName)
            argsCount += 1
            self.vmWriter.writePush('POINTER', 0)

        self.pop()  # (
        argsCount += self.compileExpressionList()
        self.pop()  # )
        print "*"*100
        print fullFunctionName
        self.vmWriter.writeCall(fullFunctionName, argsCount)

    def compileDo(self):
        """Compiles a do statement"""
        self.pop()  # do
        self.compileDoCall()
        self.pop()  # ;

        # Store return value in TEMP
        self.vmWriter.writePop('TEMP', 0)

    def compileLet(self):
        """Compiles a let statement"""
        self.pop()  # let
        varName = self.stripPop()  # varName
        varKind = self.CALL_KIND_COMPILE[self.symbolTable.kindOf(varName)]
        varIndex = self.symbolTable.indexOf(varName)

        # Handle arrays
        isArray = re.search(' \[ ', self.top())
        if isArray:
            self.pop()  # [
            self.compileExpression()
            self.pop()  # ]

            # Variable is an array, calculate destination and store it in TEMP[0]
            self.vmWriter.writePush(varKind, varIndex)
            self.vmWriter.writeArithmetic('ADD')
            self.vmWriter.writePop('TEMP', 0)

        self.pop()  # =
        self.compileExpression()
        self.pop()  # ;

        if isArray:
            # Store result in calculated destination
            self.vmWriter.writePush('TEMP', 0)
            self.vmWriter.writePop('POINTER', 1)
            self.vmWriter.writePop('THAT', 0)
        else:
            self.vmWriter.writePop(varKind, varIndex)

    def compileWhile(self):
        """Compiles a while statement"""
        self.labelIndex += 1
        whileLabel = 'WHILE_LBL_{0}'.format(self.labelIndex)
        whileendLabel = 'WHILE_END_LBL_{0}'.format(self.labelIndex)
        self.vmWriter.writeLabel(whileLabel)

        self.pop()  # while
        self.pop()  # (
        self.compileExpression()

        # If while condition is false - goto end.
        self.vmWriter.writeArithmetic('NOT')
        self.vmWriter.writeIf(whileendLabel)

        self.pop()  # )
        self.pop()  # {
        self.compileStatements()
        self.pop()  # }

        self.vmWriter.writeGoto(whileLabel)  # Loop
        self.vmWriter.writeLabel(whileendLabel)  # End of while label

    def compileReturn(self):
        """compiles a return statement."""
        self.pop()  # return

        # Handle returning an expression
        if re.search(' ; ', self.top()):
            self.vmWriter.writePush('CONST', 0)  # If no return value specified, push 0
        else:
            self.compileExpression()

        self.pop()  # ;
        self.vmWriter.writeReturn()

    def compileIf(self):
        """compiles an if statement, possibly with a trailing else clause."""
        self.labelIndex += 1
        ifLabel = 'IF_LBL_{0}'.format(self.labelIndex)
        elseLabel = 'ELSE_LBL_{0}'.format(self.labelIndex)
        ifendLabel = 'IF_END_LBL_{0}'.format(self.labelIndex)

        self.pop()  # if
        self.pop()  # (
        self.compileExpression()
        self.pop()  # )
        self.pop()  # {

        self.vmWriter.writeIf(ifLabel)
        self.vmWriter.writeGoto(elseLabel)
        self.vmWriter.writeLabel(ifLabel)
        self.compileStatements()
        self.vmWriter.writeGoto(ifendLabel)
        self.pop()  # }

        # Handle else statement
        self.vmWriter.writeLabel(elseLabel)
        if re.search(' else ', self.top()):
            self.pop()  # else
            self.pop()  # {
            self.compileStatements()
            self.pop()  # }

        self.vmWriter.writeLabel(ifendLabel)

    def compileExpression(self):
        """compiles an expression."""
        self.compileTerm()  # term

        print "OP IN EXP: " + self.top()
        while re.search(self.OP_REGEX, self.top()):
            print "OP IN EXP"
            op = self.stripPop()  # op
            self.compileTerm()  # term

            if op in self.ARITHMETIC_COMPILE:
                self.vmWriter.writeArithmetic(self.ARITHMETIC_COMPILE[op])
            else:
                self.vmWriter.writeCall(self.ARITHMETIC_BUILTIN_FUNCS[op], 2)

    def compileTerm(self):
        """Compiles a term"""
        print 'TERM\t' + self.stripTop()
        if re.search(' \( ', self.top()):
            print "EXPRESSION!"
            self.pop()  # (
            self.compileExpression()
            self.pop()  # )
        elif re.search(self.UNARY_OP_REGEX, self.top()):
            op = self.stripPop()  # unary op
            self.compileTerm()  # term (recursive call)
            self.vmWriter.writeArithmetic(self.ARITHMETIC_UNARY_COMPILE[op])
        else:
            # Term is an identifier
            topType = self.topType()
            identifier = self.stripPop()  # identifier
            if topType == CompilerConsts.INT_CONST:
                self.vmWriter.writePush('CONST', identifier)
            elif topType == CompilerConsts.STRING_CONST:
                self.pushString(identifier)
            elif topType == CompilerConsts.KEYWORD:
                self.compileKeyword(identifier)
            elif re.search(' [\.\(] ', self.top()):
                self.compileDoCall(identifier)
            else:
                print "OTHER: " + identifier
                # Variable / Subroutine
                isArray = re.search(' \[ ', self.top())
                if isArray:
                    # Variable is an array
                    self.pop()  # '['
                    self.compileExpression()  # expression
                    self.pop()  # ']'

                varKind = self.CALL_KIND_COMPILE[self.symbolTable.kindOf(identifier)]
                varIndex = self.symbolTable.indexOf(identifier)
                self.vmWriter.writePush(varKind, varIndex)

                if isArray:
                    self.vmWriter.writeArithmetic('ADD')
                    self.vmWriter.writePop('POINTER', 1)
                    self.vmWriter.writePush('THAT', 0)

    def pushString(self, st):
        """ Push a constant string """
        self.vmWriter.writePush('CONST', len(st))
        self.vmWriter.writeCall('String.new', 1)

        for ch in st:
            self.vmWriter.writePush('CONST', ord(ch))
            self.vmWriter.writeCall('String.appendChar', 2)

    def compileKeyword(self, keyword):
        if keyword == 'this':
            self.vmWriter.writePush('POINTER', 0)
        elif keyword == 'true':
            self.vmWriter.writePush('CONST', 1)
        elif keyword == 'false':
            self.vmWriter.writePush('CONST', 0)
        else:
            print "XXXXXXXXXXXXXXXXXXXXX"*100
            #TODO: ANYTHING ELSE?

    def compileExpressionList(self):
        """compiles a (possibly empty) comma separated list of expressions. """

        argCount = 0
        if not re.search(' \) ', self.top()):
            self.compileExpression()
            argCount += 1

            # Handle multiple expressions
            while re.search(' , ', self.top()):
                self.pop()  # ,
                self.compileExpression()
                argCount += 1

        return argCount
