from lxml import etree as ET
from JackTokenizer import Tokenizer
from SymbolTable import SymbolTable

"""Not certain about start_subroutine"""


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
        self.kind = None

    def compile_class(self):

        self.xmlNew = ET.Element('class')
        self.t.advance()
        self.write_token(self.xmlNew, 'class')
        # self.kind = 'class'
        self.write_token(self.xmlNew, 'IDENTIFIER',
                         kind='class', defined=True)
        self.write_token(self.xmlNew, '{')
        self.compile_class_var_dec()
        while self.t.symbol() != '}':   # subroutines
            self.compile_subroutine()
        self.write_token(self.xmlNew, '}')
        return

    def compile_class_var_dec(self):
        varKeyWords = ['field', 'static']
        name = ''
        kind = ''
        varType = ''

        while self.t.keyword() in varKeyWords:
            varNode = ET.SubElement(self.xmlNew, 'classVarDec')
            kind = self.t.tokens[self.t.tokenIndex]
            self.write_token(varNode, varKeyWords)
            # variable type
            varType = self.t.tokens[self.t.tokenIndex]
            # self.kind = 'class'
            self.write_token(varNode, ['int', 'char', 'bool', 'IDENTIFIER'],
                             kind='class')
            name = self.t.tokens[self.t.tokenIndex]
            self.symTable.define(name, varType, kind)
            # self.kind = kind
            self.write_token(varNode, 'IDENTIFIER',
                             kind=kind, defined=True)  # varName
            self.validator('SYMBOL')
            while self.t.symbol() != ';':  # checks multiple vars
                self.write_token(varNode, ',')
                name = self.t.tokens[self.t.tokenIndex]
                self.symTable.define(name, varType, kind)
                self.write_token(varNode, 'IDENTIFIER',
                                 kind=kind, defined=True)
            self.write_token(varNode, ';')
        return

    def compile_subroutine(self):

        self.subroutNode = ET.SubElement(self.xmlNew, 'subroutineDec')
        self.write_token(self.subroutNode, ['constructor', 'function',
                                            'method'])
        # self.kind = 'class'
        self.write_token(self.subroutNode, ['int', 'char',
                                            'boolean', 'void',
                                            'IDENTIFIER'], kind='class')
        # self.kind = 'subroutine'
        self.write_token(self.subroutNode, 'IDENTIFIER',
                         kind='subroutine', defined=True)
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
        name = ''
        varType = ''
        kind = ''

        paramNode = ET.SubElement(self.subroutNode, 'parameterList')
        if self.t.symbol() == ')':
            paramNode.text = '\n'
            return
        # self.kind = 'class'
        varType = self.t.tokens[self.t.tokenIndex]
        self.write_token(paramNode, ['int', 'char',
                                     'boolean', 'void',
                                     'IDENTIFIER'], kind='class')
        kind = 'arg'
        # self.kind = 'arg'
        name = self.t.tokens[self.t.tokenIndex]
        self.symTable.define(name, varType, kind)
        self.write_token(paramNode, 'IDENTIFIER',
                         kind='arg', defined=True)
        while self.t.symbol() == ',':

            self.write_token(paramNode, ',')
            # self.kind = 'class'
            self.write_token(paramNode, ['int', 'char',
                                         'boolean', 'void',
                                         'IDENTIFIER'], kind='class')
            kind = 'arg'
            # self.kind = 'arg'
            name = self.t.tokens[self.t.tokenIndex]
            self.symTable.define(name, varType, kind)
            self.write_token(paramNode, 'IDENTIFIER',
                             kind='arg', defined=True)

        return

    def compile_var_dec(self):
        name = ''
        kind = ''
        varType = ''

        while self.t.keyword() == 'var':  # check multiple lines of var
            varDecNode = ET.SubElement(self.subBodyNode, 'varDec')
            kind = 'var'
            self.write_token(varDecNode, 'var')
            varType = self.t.tokens[self.t.tokenIndex]
            # self.kind = 'class'
            self.write_token(varDecNode, ['int', 'char',
                                          'boolean', 'void',
                                          'IDENTIFIER'], kind='class')
            name = self.t.tokens[self.t.tokenIndex]
            self.symTable.define(name, varType, kind)
            # self.kind = 'var'
            self.write_token(varDecNode, 'IDENTIFIER',
                             kind='var', defined=True)  # varName

            while self.t.symbol() == ',':  # multiple varNames
                self.write_token(varDecNode, ',')
                name = self.t.tokens[self.t.tokenIndex]
                self.symTable.define(name, varType, kind)
                self.write_token(varDecNode, 'IDENTIFIER',
                                 kind='var', defined=True)

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
        "Need to implement start_subroutine"
        doNode = ET.SubElement(self.stmntNode, 'doStatement')
        savedNode = self.expressNode
        lookAhead = ''
        current_subrout_scope = self.symTable.subDict
        self.symTable.start_subroutine()
        self.write_token(doNode, 'do')
        lookAhead = self.t.tokens[self.t.tokenIndex + 1]

        if lookAhead == '(':  # subroutineName(exprlist)
            # self.kind = 'subroutine'
            self.write_token(doNode, 'IDENTIFIER', kind='subroutine')
            self.write_token(doNode, '(')
            self.expressNode = ET.SubElement(doNode, 'expressionList')
            self.compile_expression_list()
            self.expressNode = savedNode
            self.write_token(doNode, ')')
            self.write_token(doNode, ';')
            self.symTable.subDict = current_subrout_scope

            return
        else:
            # self.kind = 'class'
            self.write_token(doNode, 'IDENTIFIER', kind='class')
            self.write_token(doNode, '.')  # name.subroutine(exprList)
            # self.kind = 'subroutine'
            self.write_token(doNode, 'IDENTIFIER', kind='subroutine')
            self.write_token(doNode, '(')
            self.expressNode = ET.SubElement(doNode, 'expressionList')
            self.compile_expression_list()
            self.expressNode = savedNode
            self.write_token(doNode, ')')
            self.write_token(doNode, ';')
            self.symTable.subDict = current_subrout_scope

            return

    def compile_let(self):
        name = ''
        kind = ''
        letNode = ET.SubElement(self.stmntNode, 'letStatement')
        self.write_token(letNode, 'let')
        while self.t.symbol() != ';':
            name = self.t.identifier()
            kind = self.symTable.kind_of(name)
            # self.kind = kind
            if name in self.symTable.classDict:
                self.write_token(letNode, 'IDENTIFIER', kind=kind)
            elif name in self.symTable.subDict:
                self.write_token(letNode, 'IDENTIFIER', kind=kind)
            else:
                raise Exception(self.t.identifier() + ' is not defined')
            if self.t.symbol() == '[':  # array index
                self.write_token(letNode, '[')
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
        name = ''
        current_subrout_scope = ''

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
                name = self.t.identifier()
                # self.kind = self.symTable.kind_of(name)
                kind = self.symTable.kind_of(name)
                self.write_token(self.termNode, 'IDENTIFIER', kind=kind)
                self.write_token(self.termNode, '[')
                self.expressNode = ET.SubElement(self.termNode, 'expression')
                self.compile_expression()
                self.expressNode = savedNode
                self.write_token(self.termNode, ']')

            elif lookAhead == '(':  # subcall
                # self.kind = 'subroutine'
                current_subrout_scope = self.symTable.subDict
                self.write_token(self.termNode, 'IDENTIFIER',
                                 kind='subroutine')
                self.write_token(self.termNode, '(')
                self.expressNode = ET.SubElement(self.termNode,
                                                 'expressionList')
                self.compile_expression_list()
                self.expressNode = savedNode
                self.write_token(self.termNode, ')')
                self.symTable.subDict = current_subrout_scope

            elif lookAhead == '.':  # name.subroutName(expressList)
                # self.kind = 'class'
                current_subrout_scope = self.symTable.subDict
                self.write_token(self.termNode, 'IDENTIFIER', kind='class')
                self.write_token(self.termNode, '.')
                # self.kind = 'subroutine'
                self.write_token(self.termNode, 'IDENTIFIER',
                                 kind='subroutine')
                self.write_token(self.termNode, '(')
                self.expressNode = ET.SubElement(self.termNode,
                                                 'expressionList')
                self.compile_expression_list()
                self.expressNode = savedNode

                self.write_token(self.termNode, ')')
                self.symTable.subDict = current_subrout_scope
            else:
                name = self.t.identifier()
                # self.kind = self.symTable.kind_of(name)
                kind = self.symTable.kind_of(name)
                self.write_token(self.termNode, 'IDENTIFIER',
                                 kind=kind)  # varName

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

    def write_token(self, parent, syntax, kind=None, defined=False):
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
                self.write_variable_token(parent,
                                          kind=kind, defined=defined)
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

    def write_variable_token(self, parent, kind=None, defined=False):
        terminal = 'identifier'
        token = self.t.identifier()
        newNode = ET.SubElement(parent, terminal)
        newNode.text = token + '\n'
        newNode.text += kind + '\n'
        if kind in ['var', 'arg', 'field', 'static']:
            newNode.text += str(self.symTable.index_of(token)) + '\n'
        if defined:
            newNode.text += 'defined' + '\n'
        else:
            newNode.text += 'used' + '\n'
