from lxml import etree as ET
from JackTokenizer import Tokenizer
from SymbolTable import SymbolTable


class CompilationEngine(object):

    def __init__(self, inFile):
        self.t = Tokenizer(inFile)
        self.symTable = SymbolTable()
        self.xmlNew = None
        self.subroutNode = None
        self.subBodyNode = None
        self.stmntNode = None
        self.expressNode = None
        self.termNode = None
        self.types = ['int', 'char', 'boolean', 'void']
        self.stmnt = ['do', 'let', 'if', 'while', 'return']

    def compile_class(self):

        self.xmlNew = ET.Element('class')
        self.t.advance()
        self.write_token(self.xmlNew, 'class')
        self.write_token(self.xmlNew, 'IDENTIFIER')  # className
        self.write_token(self.xmlNew, '{')
        self.compile_class_var_dec()
        while self.t.symbol() != '}':   # subroutines
            self.compile_subroutine()
        self.write_token(self.xmlNew, '}')
        return

    def compile_class_var_dec(self):
        varKeyWords = ['field', 'static']

        while self.t.keyword() in varKeyWords:
            varNode = ET.SubElement(self.xmlNew, 'classVarDec')
            self.write_token(varNode, varKeyWords)
            # variable type
            self.write_token(varNode, ['int', 'char', 'bool', 'IDENTIFIER'])
            self.write_token(varNode, 'IDENTIFIER')  # varName

            self.validator('SYMBOL')
            while self.t.symbol() != ';':  # checks multiple vars
                self.write_token(varNode, ',')
                self.write_token(varNode, 'IDENTIFIER')
            self.write_token(varNode, ';')
        return

    def compile_subroutine(self):

        self.subroutNode = ET.SubElement(self.xmlNew, 'subroutineDec')
        self.write_token(self.subroutNode, ['constructor', 'function',
                                            'method'])
        self.write_token(self.subroutNode, ['int', 'char',
                                            'boolean', 'void',
                                            'IDENTIFIER'])
        self.write_token(self.subroutNode, 'IDENTIFIER')
        self.write_token(self.subroutNode, '(')
        self.compile_parameter_list()
        self.write_token(self.subroutNode, ')')
        self.validator('{')
        self.subBodyNode = ET.SubElement(self.subroutNode, 'subroutineBody')
        self.write_token(self.subBodyNode, '{')

        if self.t.symbol() == '}':
            self.write_token(self.subBodyNode, '}')
            return

        self.validator('KEYWORD')
        if self.t.keyword() == 'var':
            self.compile_var_dec()

        if self.t.keyword() in self.stmnt:
            self.stmntNode = ET.SubElement(self.subBodyNode, 'statements')
            self.compile_statements()

        self.write_token(self.subBodyNode, '}')

        return

    def compile_parameter_list(self):

        paramNode = ET.SubElement(self.subroutNode, 'parameterList')
        if self.t.symbol() == ')':
            paramNode.text = '\n'
            return

        self.write_token(paramNode, ['int', 'char',
                                     'boolean', 'void',
                                     'IDENTIFIER'])  # type
        self.write_token(paramNode, 'IDENTIFIER')  # varName
        while self.t.symbol() == ',':

            self.write_token(paramNode, ',')
            self.write_token(paramNode, ['int', 'char',
                                         'boolean', 'void',
                                         'IDENTIFIER'])  # type
            self.write_token(paramNode, 'IDENTIFIER')

        return

    def compile_var_dec(self):

        while self.t.keyword() == 'var':  # check multiple lines of var
            varDecNode = ET.SubElement(self.subBodyNode, 'varDec')
            self.write_token(varDecNode, 'var')
            self.write_token(varDecNode, ['int', 'char',
                                          'boolean', 'void',
                                          'IDENTIFIER'])  # type
            self.write_token(varDecNode, 'IDENTIFIER')  # varName

            while self.t.symbol() == ',':  # multiple varNames
                self.write_token(varDecNode, ',')
                self.write_token(varDecNode, 'IDENTIFIER')

            self.write_token(varDecNode, ';')

        return

    def compile_statements(self):

        while self.t.keyword() in self.stmnt:
            if self.t.keyword() == 'let':
                self.compile_let()
            elif self.t.keyword() == 'do':
                self.compile_do()
            elif self.t.keyword() == 'if':
                self.compile_if()
            elif self.t.keyword() == 'while':
                self.compile_while()
            elif self.t.keyword() == 'return':
                self.compile_return()
            else:
                raise Exception(self.t.tokens[self.t.tokenIndex] +
                                ' is not valid')

        return

    def compile_do(self):
        doNode = ET.SubElement(self.stmntNode, 'doStatement')
        savedNode = self.expressNode
        self.write_token(doNode, 'do')
        self.write_token(doNode, 'IDENTIFIER')

        if self.t.symbol() == '(':  # subroutineName(expressionlist)
            self.write_token(doNode, '(')
            self.expressNode = ET.SubElement(doNode, 'expressionList')
            self.compile_expression_list()
            self.expressNode = savedNode
            self.write_token(doNode, ')')
            self.write_token(doNode, ';')

            return

        self.write_token(doNode, '.')  # name.subroutine(exprList)
        self.write_token(doNode, 'IDENTIFIER')
        self.write_token(doNode, '(')
        self.expressNode = ET.SubElement(doNode, 'expressionList')
        self.compile_expression_list()
        self.expressNode = savedNode
        self.write_token(doNode, ')')
        self.write_token(doNode, ';')

        return

    def compile_let(self):
        letNode = ET.SubElement(self.stmntNode, 'letStatement')
        self.write_token(letNode, 'let')
        while self.t.symbol() != ';':
            self.write_token(letNode, 'IDENTIFIER')
            if self.t.symbol() == '[':  # array index
                self.write_token('letNode', '[')
                self.expressNode = ET.SubElement(letNode, 'expression')
                self.compile_expression()
                self.write_token(letNode, ']')

            self.write_token(letNode, '=')
            self.expressNode = ET.SubElement(letNode, 'expression')
            self.compile_expression()

        self.write_token(letNode, ';')

        return

    def compile_while(self):
        whileNode = ET.SubElement(self.stmntNode, 'whileStatement')
        savedNode = self.stmntNode
        self.write_token(whileNode, 'while')
        self.write_token(whileNode, '(')
        self.expressNode = ET.SubElement(whileNode, 'expression')
        self.compile_expression()

        self.write_token(whileNode, ')')
        self.write_token(whileNode, '{')

        self.stmntNode = ET.SubElement(whileNode, 'statements')
        self.compile_statements()
        self.stmntNode = savedNode

        self.write_token(whileNode, '}')

        return

    def compile_return(self):
        returnNode = ET.SubElement(self.stmntNode, 'returnStatement')
        self.write_token(returnNode, 'return')
        if self.t.symbol() == ';':
            self.write_token(returnNode, ';')
        else:
            self.expressNode = ET.SubElement(returnNode, 'expression')
            self.compile_expression()
            self.write_token(returnNode, ';')

        return

    def compile_if(self):
        savedNode = self.stmntNode  # necessary for nested statements
        ifNode = ET.SubElement(self.stmntNode, 'ifStatement')
        self.write_token(ifNode, 'if')
        self.write_token(ifNode, '(')

        self.expressNode = ET.SubElement(ifNode, 'expression')
        self.compile_expression()

        self.write_token(ifNode, ')')
        self.write_token(ifNode, '{')

        self.stmntNode = ET.SubElement(ifNode, 'statements')
        self.compile_statements()
        self.stmntNode = savedNode

        self.write_token(ifNode, '}')
        if self.t.keyword() == 'else':
            self.write_token(ifNode, 'else')
            self.write_token(ifNode, '{')

            self.stmntNode = ET.SubElement(ifNode, 'statements')
            self.compile_statements()
            self.stmntNode = savedNode

            self.write_token(ifNode, '}')

        return

    def compile_expression(self):
        op = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
        savedNode = self.termNode
        self.termNode = ET.SubElement(self.expressNode, 'term')
        self.compile_term()
        self.termNode = savedNode
        while self.t.symbol() in op:
            self.write_token(self.expressNode, op)
            self.termNode = ET.SubElement(self.expressNode, 'term')
            self.compile_term()
            self.termNode = savedNode

        return

    def compile_term(self):

        savedNode = self.expressNode
        savedOpTermNode = self.termNode
        keyConst = ['true', 'false', 'null', 'this']
        unOps = ['-', '~']
        lookAhead = ''

        if self.t.token_type() == 'INT_CONST':
            self.write_token(self.termNode, 'INT_CONST')
        elif self.t.token_type() == 'STRING_CONST':
            self.write_token(self.termNode, 'STRING_CONST')
        elif self.t.token_type() == 'KEYWORD':
            self.write_token(self.termNode, keyConst)

        elif self.t.token_type() == 'SYMBOL':
            if self.t.symbol() in unOps:  # unary operator
                self.write_token(self.termNode, unOps)
                self.termNode = ET.SubElement(self.termNode, 'term')
                self.compile_term()
                self.termNode = savedOpTermNode
            elif self.t.symbol() == '(':  # (expression))
                self.write_token(self.termNode, '(')
                self.expressNode = ET.SubElement(self.termNode, 'expression')
                self.compile_expression()
                self.expressNode = savedNode
                self.write_token(self.termNode, ')')
            else:
                raise Exception(self.t.tokens[self.t.tokenIndex] +
                                ' is not valid')
        elif self.t.token_type() == 'IDENTIFIER':  # varName, array, or subcall
            lookAhead = self.t.tokens[self.t.tokenIndex + 1]
            if lookAhead == '[':  # array item
                self.write_token(self.termNode, 'IDENTIFIER')
                self.write_token(self.termNode, '[')
                self.expressNode = ET.SubElement(self.termNode, 'expression')
                self.compile_expression()
                self.expressNode = savedNode
                self.write_token(']')

            elif lookAhead == '(':  # subcall
                self.write_token(self.termNode, 'IDENTIFIER')
                self.write_token(self.termNode, '(')
                self.expressNode = ET.SubElement(self.termNode,
                                                 'expressionList')
                self.compile_expression_list()
                self.expressNode = savedNode
                self.write_token(self.termNode, ')')

            elif lookAhead == '.':  # name.subroutName(expressList)
                self.write_token(self.termNode, 'IDENTIFIER')
                self.write_token(self.termNode, '.')
                self.write_token(self.termNode, 'IDENTIFIER')
                self.write_token(self.termNode, '(')
                self.expressNode = ET.SubElement(self.termNode,
                                                 'expressionList')
                self.compile_expression_list()
                self.expressNode = savedNode

                self.write_token(self.termNode, ')')
            else:
                self.write_token(self.termNode, 'IDENTIFIER')  # varName

        else:
            raise Exception(self.t.tokens[self.t.tokenIndex] +
                            ' is not valid')

        return

    def compile_expression_list(self):  # only in subroutineCall
        savedNode = self.expressNode
        if self.t.symbol() == ')':
            self.expressNode.text = '\n'
            return
        else:
            self.expressNode = ET.SubElement(savedNode, 'expression')
            self.compile_expression()
            while self.t.symbol() == ',':
                self.write_token(savedNode, ',')
                self.expressNode = ET.SubElement(savedNode, 'expression')
                self.compile_expression()

        return

    def validator(self, syntax):
        tokenType = self.t.token_type()
        token = self.t.tokens[self.t.tokenIndex]
        if type(syntax) != list:
            syntax = [syntax]
        for item in syntax:
            if item in [tokenType, token]:
                return True
        raise Exception(self.t.tokens[self.t.tokenIndex] +
                        ' is not valid')

    def write_token(self, parent, syntax, category=None, defined=False):
        "Started incorporating the symbol table"
        if self.validator(syntax):
            if self.t.keyword():
                terminal = 'keyword'
                newNode = ET.SubElement(parent, terminal)
                newNode.text = ' ' + self.t.keyword() + ' '
            elif self.t.symbol():
                terminal = 'symbol'
                newNode = ET.SubElement(parent, terminal)
                newNode.text = ' ' + self.t.symbol() + ' '
            elif self.t.identifier():
                if category:
                    self.write_variable_token(parent, category, defined)
                else:
                    terminal = 'identifier'
                    newNode = ET.SubElement(parent, terminal)
                    newNode.text = ' ' + self.t.identifier() + ' '
            elif self.t.string_val():
                terminal = 'stringConstant'
                newNode = ET.SubElement(parent, terminal)
                newNode.text = ' ' + self.t.string_val() + ' '
            elif self.t.int_val():
                terminal = 'integerConstant'
                newNode = ET.SubElement(parent, terminal)
                newNode.text = ' ' + self.t.int_val() + ' '
        self.t.advance()
        return

        def write_variable_token(parent, category, defined):
            terminal = 'identifier'
            newNode = ET.SubElement(parent, terminal)
            newNode.text = self.t.identifier + '\n'
            newNode.text += category + '\n'
            if defined:
                newNode.text += 'defined'
            else:
                newNode.text += 'used'
