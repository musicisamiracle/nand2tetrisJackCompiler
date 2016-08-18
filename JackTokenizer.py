import re


class Tokenizer(object):

    def __init__(self, fileName):
        self.name = fileName
        self.jackFile = open(self.name, 'r')
        self.line = ''
        self.mlComment = False
        self.tokens = []
        self.tokenIndex = 0
        self.currentToken = ''

    def get_line(self):
        self.line = self.jackFile.readline()
        if self.line == '\r\n':
            self.get_line()
        elif self.line == '':
            self.line = 'EOF'
        self.line = self.line.strip()
        return

    def strip_comments(self):
        if re.search('//', self.line):
            if re.match('//', self.line):
                self.line = ''
            else:
                self.line = re.sub('//.+', '', self.line)

        elif re.search('\/\*', self.line):
            if re.search('\/\*.+\*\/', self.line):
                self.line = re.sub('\/\*.+\*\/', '', self.line)
            else:
                self.line = re.sub('\/\*.+', '', self.line)
                self.mlComment = True
                return
        elif re.search('\*\/', self.line):
            self.line = re.sub('.*\*\/', '', self.line)
            self.mlComment = False
        else:
            if self.mlComment:
                self.line = ''

        self.line = self.line.strip()
        return

    def split_symbols(self, word):
        index = 0
        newSplit = []
        name = []
        symbols = []
        string = []
        tokenRegex = re.compile('\{|\}|\(|\)|\[|\]|\.|,|'
                                ';|\+|\-|\*|\/|&|\||<|>|=|~')

        while index < len(word):

            if tokenRegex.match(word[index]):
                symbols.append(word[index])
                name = "".join(name)
                newSplit.append(name.strip())
                name = []
                newSplit.append(word[index])
                index += 1

            elif re.match('"', word[index]):
                string.append(word[index])
                index += 1

                while index < len(word):
                    if re.match('"', word[index]):
                        string.append(word[index])
                        string = "".join(string)
                        newSplit.append(string)
                        string = []
                        index += 1
                        break
                    else:
                        string.append(word[index])
                        index += 1

            elif word[index] == ' ':
                name = "".join(name)
                newSplit.append(name)
                name = []
                index += 1
            else:
                name.append(word[index])
                index += 1

        name = "".join(name)
        newSplit.append(name)

        finalSplit = [t for t in newSplit if t != '']

        return finalSplit

    def tokenize_line(self):
        self.get_line()
        self.strip_comments()
        self.tokens = self.split_symbols(self.line)
        if not self.tokens:
            self.tokenize_line()
        self.tokenIndex = 0
        return

    def has_more_tokens(self):
        """parsing after advancing makes length - 1 necessary"""
        if self.tokenIndex < len(self.tokens) - 1:
            return True
        else:
            return False

    def advance(self):
        if self.has_more_tokens():
            self.tokenIndex += 1
        else:
            self.tokenize_line()
        self.currentToken = self.tokens[self.tokenIndex]
        return

    def token_type(self):
        keyword = ['class', 'constructor', 'function', 'method', 'field',
                   'static', 'var', 'int', 'char', 'boolean', 'void', 'true',
                   'false', 'null', 'this', 'let', 'do', 'if',
                   'else', 'while', 'return']
        symbol = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*',
                  '/', '&', '|', '<', '>', '=', '~']

        if self.tokens[self.tokenIndex] in keyword:
            return 'KEYWORD'
        elif self.tokens[self.tokenIndex] in symbol:
            return 'SYMBOL'
        elif re.match('[0-9]', self.tokens[self.tokenIndex]):
            if int(self.tokens[self.tokenIndex]) in range(0, 32768):
                return 'INT_CONST'
        elif re.match('".*"', self.tokens[self.tokenIndex]):
            return 'STRING_CONST'
        elif re.match('[A-Za-z_]+', self.tokens[self.tokenIndex]):
            return 'IDENTIFIER'
        else:
            return self.tokens[self.tokenIndex] + ' is not a valid token'

    def keyword(self):
        if self.token_type() == 'KEYWORD':
            return self.tokens[self.tokenIndex]

    def symbol(self):
        if self.token_type() == 'SYMBOL':
            return self.tokens[self.tokenIndex]

    def identifier(self):
        if self.token_type() == 'IDENTIFIER':
            return self.tokens[self.tokenIndex]

    def int_val(self):
        if self.token_type() == 'INT_CONST':
            return self.tokens[self.tokenIndex]

    def string_val(self):
        if self.token_type() == 'STRING_CONST':
            return self.tokens[self.tokenIndex].strip('"')

    def current_token(self):
        return self.currentToken

    def close(self):
        self.jackFile.close()
        return
