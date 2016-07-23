

class SymbolTable(object):

    def __init__(self):
        self.classDict = {}
        self.subDict = {}
        self.staticIndex = 0
        self.fieldIndex = 0
        self.argIndex = 0
        self.varIndex = 0

    def start_subroutine(self):  # need to consider nesting functions
        self.subDict = {}
        self.argIndex = 0
        self.varIndex = 0
        return

    def define(self, name, type, kind):
        if kind == 'static':
            self.classDict[name] = {'type': type,
                                    'kind': kind,
                                    'index': self.staticIndex}
            self.staticIndex += 1
        elif kind == 'field':
            self.classDict[name] = {'type': type,
                                    'kind': kind,
                                    'index': self.fieldIndex}
            self.fieldIndex += 1
        elif kind == 'arg':
            kind = 'argument'
            self.subDict[name] = {'type': type,
                                  'kind': kind,
                                  'index': self.argIndex}
            self.argIndex += 1
        elif kind == 'var':
            kind = 'local'
            self.subDict[name] = {'type': type,
                                  'kind': kind,
                                  'index': self.varIndex}
            self.varIndex += 1
        else:
            raise Exception(name + ' is not a variable')
        return

    def var_count(self, kind):
        if kind == 'static':
            return self.staticIndex
        elif kind == 'field':
            return self.fieldIndex
        elif kind == 'arg':
            return self.argIndex
        elif kind == 'var':
            return self.varIndex
        else:
            return None

    def kind_of(self, name):
        if name in self.classDict:
            return self.classDict[name]['kind']
        elif name in self.subDict:
            return self.subDict[name]['kind']

    def type_of(self, name):
        if name in self.classDict:
            return self.classDict[name]['type']
        elif name in self.subDict:
            return self.subDict[name]['type']

    def index_of(self, name):
        if name in self.classDict:
            return self.classDict[name]['index']
        elif name in self.subDict:
            return self.subDict[name]['index']
