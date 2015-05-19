
class CompilationEngine:
    '''This module effects the actual compilation into XML form.
    It gets its input from a JackTokenizer and writes its parsed XML structure into an output file/stream.
    This is done by a series of compilexxx() methods, where xxx is a corresponding syntactic element of the
    Jack grammar. The contract between these methods is that each compilexxx() method should read the
    syntactic construct xxx from the input, advance() the tokenizer exactly beyond xxx, and output the XML
    parsing of xxx. Thus, compilexxx() may only be called if indeed xxx is the next syntactic element of
    the input.'''

    STATEMENT_REGEX = ' (letStatement) | (ifStatement) | (whileStatement) | (doStatement) | (returnStatement) '
    OP_REGEX = r'> (\+|-|\*|/|&amp;|\||&lt;|&gt;|=) <'
    UNARY_OP_REGEX = r'> (-|~) <'

    def __init__(self, inputXmlTokens, outFile):
      self.input = inputXmlTokens
      self.outFile = outFile
      self.indentLevel = 0

    def write(self, txt):
        self.outFile.write('  ' * self.indentLevel)
        self.outFile.write(txt)
        self.outFile.write('\n')

    def indent(self):
        self.indentLevel += 1

    def deindent(self):
        self.indentLevel -= 1

    def pop(self):
        return self.input.pop(0)

    def top(self):
        return self.input[0]

    def writePop(self):
        self.writePop()

    def writeAndIndent(self, txt):
        self.write(txt)
        self.indent();

    def deindentAndWrite(self, txt):
        self.deindent();
        self.write(txt)

    def compileClass(self):
    	'''compiles a complete class.'''
        self.writeAndIndent('<class>')
        self.writePop() # class keyword
        self.writePop() # class name
        self.writePop() # {

        # Write class fields
        while re.search('static|field', self.top()):
            self.compileClassVarDec()

        # Write class methods
        while re.search('constructor|function|method', self.top()):
            self.compileSubroutine()

        self.writePop() # }
        self.deindentAndWrite('</class>')

    def compileClassVarDec(self):
    	'''compiles a static declaration or a field declaration.'''
        self.writeAndIndent('<classVarDec>')
        self.writePop() # var keyword
        self.writePop() # type
        self.writePop() # variable name

        # Compile additional comma-separated variables
        while re.search(' , ', self.top()):
            self.writePop() # ,
            self.writePop() # variable name

        self.writePop() # ;
        self.deindentAndWrite('</classVarDec>')

    def compileSubroutine(self):
    	'''compiles a complete method, function, or constructor.'''
        self.writeAndIndent('<subroutineDec>')
        self.writePop() # subroutine keyword
        self.writePop() # type
        self.writePop() # subroutine name
        self.writePop() # (
        self.compileParameterList()
        self.writePop() # )

        self.writeAndIndent('<subroutineBody>')
        self.writePop() # {

        # Compile all subroutine variables
        while re.search(' var ', self.top()):
            self.compileVarDec() # subroutine variable declarations

        self.compileStatements() # subroutine body statements
        self.writePop() # }
        self.deindentAndWrite('</subroutineBody>')

        self.deindentAndWrite('</subroutineDec>')

    def compileParameterList(self):
    	'''compiles a (possibly empty) parameter list, not including the enclosing ().'''
        self.writeAndIndent('<parameterList>')

        if not re.search(' ) ', self.top()):
            self.writePop() # var type
            self.writePop() # var name

            while re.search(' , ', self.top()):
                self.writePop() # ,
                self.writePop() # var type
                self.writePop() # var name

        self.deindentAndWrite('</parameterList>')

    def compileVarDec(self):
    	'''compiles a var declaration.'''
        self.writeAndIndent('<varDec>')
        self.writePop() # var
        self.writePop() # type
        self.writePop() # var name

        # Compile additional variables of same type
        while re.search(' , ', self.top()):
            self.writePop() # ,
            self.writePop() # var name

        self.writePop() # ;
        self.deindentAndWrite('</varDec>')

    def compileStatements(self):
    	'''compiles a sequence of statements, not including the enclosing {}.'''
        self.writeAndIndent('<statements>')

        # Compile all consecutive statements
        while re.search(STATEMENT_REGEX, self.top()):
            group = re.search(STATEMENT_REGEX, self.top()).group()
            if group == 'letStatement':
                self.compileLet()
            elif group == 'ifStatement':
                self.compileIf()
            elif group == 'whileStatement':
                self.compileWhile()
            elif group == 'doStatement':
                self.compileDo()
            elif group == 'returnStatement':
                self.compileReturn()
            else:
                print "Unknown group"
        self.deindentAndWrite('</statements>')

    def compileDo(self):
    	'''Compiles a do statement'''
        self.writeAndIndent('<doStatement>')
        self.writePop() # do
        self.writePop() # subroutine call / variable/class name

        # Handle sub-variables / class calls
        if re.search(' . ', self.top()):
            self.writePop() # .
            self.writePop() # subroutine call

        self.writePop() # (
        self.compileExpressionList()
        self.writePop() # )
        self.writePop() # ;
        self.deindentAndWrite('</doStatement>')

    def compileLet(self):
    	'''Compiles a let statement'''
        self.writeAndIndent('<letStatement>')
        self.writePop() # let
        self.writePop() # varName

        # Handle variable with expressions
        if re.search(' [ ', self.top()):
            self.writePop() # [
            self.compileExpression()
            self.writePop() # ]

        self.writePop() # =
        self.compileExpression()
        self.writePop() # ;
        self.deindentAndWrite('</letStatement>')

    def compileWhile(self):
    	'''Compiles a while statement'''
        self.writeAndIndent('<whileStatement>')
        self.writePop() # while
        self.writePop() # (
        self.compileExpression()
        self.writePop() # )
        self.writePop() # {
        self.compileStatements()
        self.writePop() # }
        self.deindentAndWrite('</whileStatement>')

    def compileReturn(self):
    	'''compiles a return statement.'''
        self.writeAndIndent('<returnStatement>')
        self.writePop() # return

        # Handle returning an expression
        if not re.search(' ; ', self.top()):
            self.compileExpression()

        self.writePop() # ;
        self.deindentAndWrite('</returnStatement>')

    def compileIf(self):
    	'''compiles an if statement, possibly with a trailing else clause.'''
        self.writeAndIndent('<ifStatement>')
        self.writePop() # if
        self.writePop() # (
        self.compileExpression()
        self.writePop() # )
        self.writePop() # {
        self.compileStatements()
        self.writePop() # }

        # Handle else statement
        if re.search(' else ', self.top()):
            self.writePop() # else
            self.writePop() # {
            self.compileStatements()
            self.writePop() # }

        self.deindentAndWrite('</ifStatement>')

    def compileExpression(self):
    	'''compiles an expression.'''
        self.writeAndIndent('<expression>')
        self.compileTerm() # term

        while re.search(OP_REGEX, self.top()):
            self.writePop() # op
            self.compileTerm() # term

        self.deindentAndWrite('</expression>')

    def compileTerm(self):
        '''Compiles a term'''
        self.writeAndIndent('<term>')
        if re.search(' ( ', self.top()):
            self.writePop() # (
            self.compileExpression()
            self.writePop() # )
        elif re.search(UNARY_OP_REGEX, self.top()):
            self.writePop() # unary op
            self.compileTerm() # term (recursive call)
        else:
            # Term is an identifier
            self.writePop() # identifier
            if re.search(' [ ', self.top()):
                self.writePop() # [
                self.compileExpression()
                self.writePop() # ]
            else:
                if re.search(' . ', self.top()):
                    self.writePop() # .
                    self.writePop() # subroutine call

                self.writePop() # (
                self.compileExpressionList()
                self.writePop() # )

        self.deindentAndWrite('</term>')


    def compileExpressionList(self):
        '''compiles a (possibly empty) commaseparated list of expressions. '''
        self.writeAndIndent('<expressionList>')

        if not re.search(' ) ', self.top()):
            self.compileExpression()

            # Handle multiple expressions
            while re.search(' , ', self.top()):
                self.writePop() # ,
                self.compileExpression()

        self.deindentAndWrite('</expressionList>')
