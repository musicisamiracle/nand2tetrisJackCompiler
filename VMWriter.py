

class VMWriter(object):

    def __init__(self, outFileName):
        self.vmFile = open(outFileName, 'w')

    def write_push(self, segment, index):
        self.vmFile.write('push ' + segment + ' ' + str(index) + '\n')

    def write_pop(self, segment, index):
        self.vmFile.write('pop ' + segment + ' ' + str(index) + '\n')

    def write_arithmetic(self, command, neg=False):
        op = {'+': 'add', '*': 'call Math.multiply 2',
              '/': 'call Math.divide 2', '&': 'and', '|': 'or', '<': 'lt',
              '>': 'gt', '=': 'eq', '~': 'not'}
        if command == '-':
            if neg:
                self.vmFile.write('neg\n')
            else:
                self.vmFile.write('sub\n')
        else:
            self.vmFile.write(op[command] + '\n')

    def write_label(self, label):
        self.vmFile.write('label ' + label + '\n')

    def write_goto(self, label):
        self.vmFile.write('goto ' + label + '\n')

    def write_if(self, label):
        self.vmFile.write('if-goto ' + label + '\n')

    def write_call(self, name, numArgs):
        self.vmFile.write('call ' + name + ' ' + str(numArgs) + '\n')

    def write_function(self, name, numLocals):
        self.vmFile.write('function ' + name + ' ' + str(numLocals) + '\n')

    def write_return(self):
        self.vmFile.write('return\n')

    def close(self):
        self.vmFile.close()
