extra stuff

class VMWriter(object):

    def __init__(self):  # add outFileName
        # self.vmFile = open(outFileName, 'w')
        self.debugOut = ''

    def write_push(self, segment, index):
        self.debugOut += 'push ' + segment + ' ' + index + '\n'

    def write_pop(self, segment, index):
        self.debugOut += 'pop ' + segment + ' ' + index + '\n'

    def write_arithmetic(self, command):  # not sure how to do neg
        op = {'+': 'add', '-': ['sub', 'neg'], '*': 'call Math.multiply 2',
              '/': 'call Math.divide 2', '&': 'and', '|': 'or', '<': 'lt',
              '>': 'gt', '=': 'eq', '~': 'not'}
        if command == '-':
            pass
        else:
            self.debugOut += op[command] + '\n'

    def write_label(self, label):
        self.debugOut += 'label ' + label + '\n'

    def write_goto(self, label):
        self.debugOut += 'goto ' + label + '\n'

    def write_if(self, label):
        self.debugOut += 'if-goto ' + label + '\n'

    def write_call(self, name, numArgs):
        self.debugOut += 'call ' + name + ' ' + numArgs + '\n'

    def write_function(self, name, numLocals):
        self.debugOut += 'function ' + name + ' ' + numLocals + '\n'

    def write_return(self):
        self.debugOut += 'return\n'

    def write_close(self):
        # self.vmFile.close()
        pass

v = VMWriter()
v.write_push('static', '0')
v.write_pop('field', '1')
v.write_arithmetic('+')
v.write_label('END')
v.write_goto('END')
v.write_if('NOW')
v.write_call('Awesome.test', '1')
v.write_function('Awesome.test', '1')
v.write_return()
print v.debugOut
