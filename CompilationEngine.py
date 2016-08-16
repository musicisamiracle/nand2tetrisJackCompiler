from lxml import etree as ET
from JackTokenizer import Tokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter


class CompilationEngine(object):

    def __init__(self, inFile):
        self.t = Tokenizer(inFile)
        self.symTable = SymbolTable()
        self.vmName = inFile.rstrip('.jack') + '.vm'
        self.vm = VMWriter(self.vmName)
        self.className = ''
        self.xmlNew = None
        self.subroutNode = None
        self.subBodyNode = None
        self.stmntNode = None
        self.expressNode = None
        self.termNode = None
        self.types = ['int', 'char', 'boolean', 'void']
        self.stmnt = ['do', 'let', 'if', 'while', 'return']
        self.subroutType = ''
        self.whileIndex = 0
        self.ifIndex = 0
        self.fieldNum = 0

    def compile_class(self):

        self.xmlNew = ET.Element('class')
        self.t.advance()
        self.write_token(self.xmlNew, 'class')
        self.className = self.t.currentToken
        self.write_token(self.xmlNew, 'IDENTIFIER',
                         kind='class', defined=True)
        self.write_token(self.xmlNew, '{')
        self.fieldNum = self.compile_class_var_dec()
        while self.t.symbol() != '}':   # subroutines
            self.compile_subroutine()
        self.write_token(self.xmlNew, '}')
        self.vm.close()
        return

    def compile_class_var_dec(self):
        varKeyWords = ['field', 'static']
        name = ''
        kind = ''
        varType = ''
        counter = 0
        while self.t.keyword() in varKeyWords:
            varNode = ET.SubElement(self.xmlNew, 'classVarDec')
            kind = self.t.currentToken
            self.write_token(varNode, varKeyWords)
            # variable type
            varType = self.t.currentToken
            self.write_token(varNode, ['int', 'char', 'boolean', 'IDENTIFIER'],
                             kind='class')
            name = self.t.currentToken
            self.symTable.define(name, varType, kind)
            self.write_token(varNode, 'IDENTIFIER',
                             kind=kind, defined=True)  # varName
            if kind == 'field':
                counter += 1

            self.validator('SYMBOL')
            while self.t.symbol() != ';':  # checks multiple vars
                self.write_token(varNode, ',')
                name = self.t.currentToken
                self.symTable.define(name, varType, kind)
                self.write_token(varNode, 'IDENTIFIER',
                                 kind=kind, defined=True)
                if kind == 'field':
                    counter += 1
            self.write_token(varNode, ';')
        return counter

    def compile_subroutine(self):
        current_subrout_scope = self.symTable.subDict
        self.symTable.start_subroutine()

        self.subroutNode = ET.SubElement(self.xmlNew, 'subroutineDec')

        subroutKword = self.t.currentToken
        self.write_token(self.subroutNode, ['constructor', 'function',
                                            'method'])

        self.subroutType = self.t.currentToken
        self.write_token(self.subroutNode, ['int', 'char',
                                            'boolean', 'void',
                                            'IDENTIFIER'], kind='class')

        name = self.t.currentToken
        subroutName = self.className + '.' + name
        self.write_token(self.subroutNode, 'IDENTIFIER',
                         kind='subroutine', defined=True)
        self.write_token(self.subroutNode, '(')

        if subroutKword == 'method':
            self.compile_parameter_list(method=True)
        else:
            self.compile_parameter_list()

        self.write_token(self.subroutNode, ')')
        self.validator('{')
        self.subBodyNode = ET.SubElement(self.subroutNode, 'subroutineBody')
        self.write_token(self.subBodyNode, '{')

        if self.t.symbol() == '}':
            self.write_token(self.subBodyNode, '}')
            return

        self.validator('KEYWORD')
        numLocals = 0
        if self.t.keyword() == 'var':
            numLocals = self.compile_var_dec()

        self.vm.write_function(subroutName, numLocals)

        if subroutKword == 'constructor':
            self.vm.write_push('constant', self.fieldNum)
            self.vm.write_call('Memory.alloc', 1)
            self.vm.write_pop('pointer', 0)
        elif subroutKword == 'method':
            self.vm.write_push('argument', 0)
            self.vm.write_pop('pointer', 0)

        if self.t.keyword() in self.stmnt:
            self.stmntNode = ET.SubElement(self.subBodyNode, 'statements')
            self.compile_statements()

        self.write_token(self.subBodyNode, '}')
        self.symTable.subDict = current_subrout_scope
        self.whileIndex = 0
        self.ifIndex = 0
        return

    def compile_parameter_list(self, method=False):
        name = ''
        varType = ''
        kind = ''
        counter = 0

        paramNode = ET.SubElement(self.subroutNode, 'parameterList')
        if self.t.symbol() == ')':
            paramNode.text = '\n'
            return counter
        varType = self.t.currentToken
        self.write_token(paramNode, ['int', 'char',
                                     'boolean', 'void',
                                     'IDENTIFIER'], kind='class')
        kind = 'arg'
        name = self.t.currentToken
        if method:
            self.symTable.define(name, varType, kind, method=True)
        else:
            self.symTable.define(name, varType, kind)

        self.write_token(paramNode, 'IDENTIFIER',
                         kind='arg', defined=True)
        counter += 1
        while self.t.symbol() == ',':

            self.write_token(paramNode, ',')
            self.write_token(paramNode, ['int', 'char',
                                         'boolean', 'void',
                                         'IDENTIFIER'], kind='class')
            kind = 'arg'
            name = self.t.currentToken
            self.symTable.define(name, varType, kind)
            self.write_token(paramNode, 'IDENTIFIER',
                             kind='arg', defined=True)
            counter += 1
        return counter

    def compile_var_dec(self):
        name = ''
        kind = ''
        varType = ''
        counter = 0

        while self.t.keyword() == 'var':  # check multiple lines of var
            varDecNode = ET.SubElement(self.subBodyNode, 'varDec')
            kind = 'var'
            self.write_token(varDecNode, 'var')
            varType = self.t.currentToken
            self.write_token(varDecNode, ['int', 'char',
                                          'boolean', 'void',
                                          'IDENTIFIER'], kind='class')
            name = self.t.currentToken
            self.symTable.define(name, varType, kind)
            self.write_token(varDecNode, 'IDENTIFIER',
                             kind='var', defined=True)  # varName
            counter += 1

            while self.t.symbol() == ',':  # multiple varNames
                self.write_token(varDecNode, ',')
                name = self.t.currentToken
                self.symTable.define(name, varType, kind)
                self.write_token(varDecNode, 'IDENTIFIER',
                                 kind='var', defined=True)
                counter += 1
            self.write_token(varDecNode, ';')

        return counter

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
                raise Exception(self.t.currentToken +
                                ' is not valid')

        return

    def compile_do(self):
        doNode = ET.SubElement(self.stmntNode, 'doStatement')
        savedNode = self.expressNode
        lookAhead = ''
        self.write_token(doNode, 'do')
        lookAhead = self.t.tokens[self.t.tokenIndex + 1]

        if lookAhead == '(':  # subroutineName(exprlist)
            subroutName = self.className + '.' + self.t.currentToken
            self.write_token(doNode, 'IDENTIFIER', kind='subroutine')

            self.write_token(doNode, '(')
            self.expressNode = ET.SubElement(doNode, 'expressionList')

            self.vm.write_push('pointer', 0)
            numArgs = self.compile_expression_list()
            self.vm.write_call(subroutName, numArgs + 1)  # add 1 for 'this'

            self.expressNode = savedNode
            self.write_token(doNode, ')')
            self.write_token(doNode, ';')
            self.vm.write_pop('temp', 0)  # throws away returned value
            return
        else:
            className = self.t.currentToken
            self.write_token(doNode, 'IDENTIFIER', kind='class')

            self.write_token(doNode, '.')  # name.subroutine(exprList)
            subroutName = self.t.currentToken
            self.write_token(doNode, 'IDENTIFIER', kind='subroutine')

            self.write_token(doNode, '(')
            self.expressNode = ET.SubElement(doNode, 'expressionList')

            if self.symTable.kind_of(className) in ['this', 'static',
                                                    'local', 'argument']:
                # used 'this' for 'field'
                typeName = self.symTable.type_of(className)
                subroutName = typeName + '.' + subroutName
                segment = self.symTable.kind_of(className)
                index = self.symTable.index_of(className)
                self.vm.write_push(segment, index)
                numArgs = self.compile_expression_list()
                self.vm.write_call(subroutName, numArgs + 1)
            else:
                subroutName = className + '.' + subroutName
                numArgs = self.compile_expression_list()
                self.vm.write_call(subroutName, numArgs)

            self.expressNode = savedNode
            self.write_token(doNode, ')')
            self.write_token(doNode, ';')
            self.vm.write_pop('temp', 0)
            return

    def compile_let(self):
        name = ''
        kind = ''
        array = False
        letNode = ET.SubElement(self.stmntNode, 'letStatement')
        self.write_token(letNode, 'let')
        while self.t.symbol() != ';':
            name = self.t.identifier()
            kind = self.symTable.kind_of(name)
            index = self.symTable.index_of(name)
            # need to write next if statement better. Need to verify in scope.
            if name in self.symTable.classDict:
                self.write_token(letNode, 'IDENTIFIER', kind=kind)
            elif name in self.symTable.subDict:
                self.write_token(letNode, 'IDENTIFIER', kind=kind)
            else:
                raise Exception(self.t.identifier() + ' is not defined')
            if self.t.symbol() == '[':  # array index
                array = True
                """if there are issues with arrays later, look here"""
                self.vm.write_push(kind, index)
                self.write_token(letNode, '[')
                self.expressNode = ET.SubElement(letNode, 'expression')
                self.compile_expression()
                self.write_token(letNode, ']')
                self.vm.write_arithmetic('+')

            self.write_token(letNode, '=')
            self.expressNode = ET.SubElement(letNode, 'expression')
            self.compile_expression()
            if array:
                self.vm.write_pop('temp', 0)
                self.vm.write_pop('pointer', 1)
                self.vm.write_push('temp', 0)
                self.vm.write_pop('that', 0)
            else:
                self.vm.write_pop(kind, index)
        self.write_token(letNode, ';')

        return

    def compile_while(self):
        whileNode = ET.SubElement(self.stmntNode, 'whileStatement')
        savedNode = self.stmntNode
        currentWhile = 'WHILE' + str(self.whileIndex)
        self.vm.write_label(currentWhile)
        self.whileIndex += 1
        self.write_token(whileNode, 'while')
        self.write_token(whileNode, '(')
        self.expressNode = ET.SubElement(whileNode, 'expression')
        self.compile_expression()
        self.vm.write_arithmetic('~')
        self.vm.write_if('END' + currentWhile)
        self.write_token(whileNode, ')')
        self.write_token(whileNode, '{')

        self.stmntNode = ET.SubElement(whileNode, 'statements')
        self.compile_statements()
        self.vm.write_goto(currentWhile)
        self.stmntNode = savedNode

        self.write_token(whileNode, '}')
        self.vm.write_label('END' + currentWhile)
        return

    def compile_return(self):
        returnNode = ET.SubElement(self.stmntNode, 'returnStatement')
        self.write_token(returnNode, 'return')
        if self.t.symbol() == ';':
            self.write_token(returnNode, ';')

            if self.subroutType == 'void':
                self.vm.write_push('constant', '0')
                self.vm.write_return()
        else:
            # self.expressNode = ET.SubElement(returnNode, 'expression')
            self.compile_expression()
            # self.write_token(returnNode, ';')
            self.validator(';')
            self.t.advance()
            self.vm.write_return()

        return

    def compile_if(self):  # noXML
        endIf = 'END_IF' + str(self.ifIndex)
        currentElse = 'IF_ELSE' + str(self.ifIndex)
        self.ifIndex += 1
        self.t.advance()
        self.validator('(')
        self.t.advance()
        self.compile_expression()
        self.vm.write_arithmetic('~')
        self.vm.write_if(currentElse)

        self.validator(')')
        self.t.advance()
        self.validator('{')
        self.t.advance()

        self.compile_statements()
        self.vm.write_goto(endIf)
        self.validator('}')
        self.t.advance()
        self.vm.write_label(currentElse)

        if self.t.keyword() == 'else':
            self.t.advance()
            self.validator('{')
            self.t.advance()

            self.compile_statements()

            self.validator('}')
            self.t.advance()
        self.vm.write_label(endIf)
        return

    def compile_expression(self):  # noXML
        op = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
        self.compile_term()
        while self.t.symbol() in op:
            opToken = self.t.currentToken
            self.t.advance()
            self.compile_term()
            self.vm.write_arithmetic(opToken)
        return

    def compile_term(self):  # noXML

        keyConst = ['true', 'false', 'null', 'this']
        unOps = ['-', '~']
        lookAhead = ''
        name = ''
        current_subrout_scope = ''

        if self.t.token_type() == 'INT_CONST':
            self.vm.write_push('constant', self.t.currentToken)
            self.t.advance()
        elif self.t.token_type() == 'STRING_CONST':
            string = self.t.currentToken.strip('"')
            length = len(string)
            self.vm.write_push('constant', length)
            self.vm.write_call('String.new', 1)
            for char in string:
                char = ord(char)  # gives the ASCII number
                self.vm.write_push('constant', char)
                self.vm.write_call('String.appendChar', 2)
            self.t.advance()

        elif self.t.token_type() == 'KEYWORD':
            self.validator(keyConst)
            if self.t.currentToken in ['false', 'null']:
                self.t.advance()
                self.vm.write_push('constant', '0')
            elif self.t.currentToken == 'true':
                self.vm.write_push('constant', '1')
                self.vm.write_arithmetic('-', neg=True)
                self.t.advance()
            else:
                self.vm.write_push('pointer', '0')
                self.t.advance()

        elif self.t.token_type() == 'SYMBOL':
            if self.t.symbol() in unOps:  # unary operator
                unOpToken = self.t.currentToken
                self.t.advance()
                self.compile_term()
                self.vm.write_arithmetic(unOpToken, neg=True)
            elif self.t.symbol() == '(':  # (expression))
                self.t.advance()
                self.compile_expression()
                self.t.advance()
            else:
                raise Exception(self.t.currentToken +
                                ' is not valid')
        elif self.t.token_type() == 'IDENTIFIER':  # varName, array, or subcall
            lookAhead = self.t.tokens[self.t.tokenIndex + 1]
            if lookAhead == '[':  # array item
                name = self.t.identifier()
                kind = self.symTable.kind_of(name)
                index = self.symTable.index_of(name)
                if name in self.symTable.classDict:
                    self.t.advance()
                elif name in self.symTable.subDict:
                    self.t.advance()
                else:
                    raise Exception(self.t.identifier() + ' is not defined')
                self.vm.write_push(kind, index)
                self.validator('[')
                self.t.advance()
                self.compile_expression()

                self.vm.write_arithmetic('+')
                self.vm.write_pop('pointer', 1)
                self.vm.write_push('that', 0)

                self.validator(']')
                self.t.advance()

            elif lookAhead == '(':  # subcall
                current_subrout_scope = self.symTable.subDict
                name = self.className + '.' + self.t.currentToken
                self.t.advance()
                self.validator('(')
                self.t.advance()
                numArgs = self.compile_expression_list()
                self.vm.write_call(name, numArgs + 1)
                self.validator(')')
                self.t.advance()
                self.symTable.subDict = current_subrout_scope

            elif lookAhead == '.':  # name.subroutName(expressList)
                current_subrout_scope = self.symTable.subDict
                className = self.t.currentToken
                self.t.advance()
                self.validator('.')
                self.t.advance()
                self.validator('IDENTIFIER')
                subroutName = self.t.currentToken
                self.t.advance()
                name = className + '.' + subroutName
                self.validator('(')
                self.t.advance()
                if self.symTable.kind_of(className) in ['this', 'static',
                                                        'local', 'argument']:
                    # used 'this' for 'field'
                    classType = self.symTable.type_of(className)
                    name = classType + '.' + subroutName
                    kind = self.symTable.kind_of(className)
                    index = self.symTable.index_of(className)
                    self.vm.write_push(kind, index)
                    numArgs = self.compile_expression_list()
                    self.vm.write_call(name, numArgs + 1)
                else:
                    numArgs = self.compile_expression_list()
                    self.vm.write_call(name, numArgs)
                self.validator(')')
                self.t.advance()
                self.symTable.subDict = current_subrout_scope
            else:
                name = self.t.identifier()  # varName
                kind = self.symTable.kind_of(name)
                index = self.symTable.index_of(name)
                self.vm.write_push(kind, index)
                self.t.advance()
        else:
            raise Exception(self.t.currentToken +
                            ' is not valid')

        return

    def compile_expression_list(self):  # only in subroutineCall  noXML
        counter = 0
        if self.t.symbol() == ')':
            return counter
        else:
            self.compile_expression()
            counter += 1
            while self.t.symbol() == ',':
                self.t.advance()
                self.compile_expression()
                counter += 1

        return counter

    def validator(self, syntax):
        tokenType = self.t.token_type()
        token = self.t.currentToken
        if type(syntax) != list:
            syntax = [syntax]
        for item in syntax:
            if item in [tokenType, token]:
                return True
        raise Exception(self.t.currentToken +
                        ' is not valid')

    def write_token(self, parent, syntax, kind=None, defined=False):
        if self.validator(syntax):
            pass
        self.t.advance()
        return
