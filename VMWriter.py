

class VMWriter(object):

    segment = ['CONST', 'ARG', 'LOCAL', 'STATIC',
               'THIS', 'THAT', 'POINTER', 'TEMP']

    def __init__(self, outFileName):
        self.vmFile = open(outFileName, 'w')
        self.debugOut = ''

        def write_push(segment, index):
            self.debugOut += 'push ' + segment + ' ' + index + '\n'

        def write_pop(segment, index):
            self.debugOut += 'pop ' + segment + ' ' + index + '\n'

        def write_arithmetic(command):
            pass

        def write_label(label):
            pass

        def write_goto(label):
            pass

        def write_if(label):
            pass

        def write_call(name, numArgs):
            pass

        def write_function(name, numLocals):
            pass

        def write_return():
            pass

        def write_close():
            self.vmFile.close()
