

class VMWriter(object):

    def __init__(self, outFileName):  # add outFileName
        self.vmFile = open(outFileName, 'w')
        self.debugOut = ''

    def write_push(self, segment, index):
        self.debugOut += 'push ' + segment + ' ' + str(index) + '\n'
        self.vmFile.write('push ' + segment + ' ' + str(index) + '\n')

    def write_pop(self, segment, index):
        self.debugOut += 'pop ' + segment + ' ' + str(index) + '\n'
        self.vmFile.write('pop ' + segment + ' ' + str(index) + '\n')

    def write_arithmetic(self, command, neg=False):  # not sure how to do neg
        op = {'+': 'add', '*': 'call Math.multiply 2',
              '/': 'call Math.divide 2', '&': 'and', '|': 'or', '<': 'lt',
              '>': 'gt', '=': 'eq', '~': 'not'}
        if command == '-':
            if neg:
                self.debugOut += 'neg\n'
                self.vmFile.write('neg\n')
            else:
                self.debugOut += 'sub\n'
                self.vmFile.write('sub\n')
        else:
            self.debugOut += op[command] + '\n'
            self.vmFile.write(op[command] + '\n')

    def write_label(self, label):
        self.debugOut += 'label ' + label + '\n'
        self.vmFile.write('label ' + label + '\n')

    def write_goto(self, label):
        self.debugOut += 'goto ' + label + '\n'
        self.vmFile.write('goto ' + label + '\n')

    def write_if(self, label):
        self.debugOut += 'if-goto ' + label + '\n'
        self.vmFile.write('if-goto ' + label + '\n')

    def write_call(self, name, numArgs):
        self.debugOut += 'call ' + name + ' ' + str(numArgs) + '\n'
        self.vmFile.write('call ' + name + ' ' + str(numArgs) + '\n')

    def write_function(self, name, numLocals):
        self.debugOut += 'function ' + name + ' ' + str(numLocals) + '\n'
        self.vmFile.write('function ' + name + ' ' + str(numLocals) + '\n')

    def write_return(self):
        self.debugOut += 'return\n'
        self.vmFile.write('return\n')

    def close(self):
        self.vmFile.close()
