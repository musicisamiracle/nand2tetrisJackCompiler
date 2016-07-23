import CompilationEngine as CE
import sys
import glob
import os

"""Need to change access to class variables into class methods"""

try:
    c = CE.CompilationEngine('ConvertToBin/Main.jack')
    c.compile_class()
    print c.vm.debugOut
except:
    raise


"""def main():

    script, fileName = sys.argv
    fileName = fileName
    isDirectory = False

    if fileName.endswith('.jack'):
        c = CE.CompilationEngine(fileName)
    else:
        try:
            os.chdir(fileName)
            isDirectory = True
        except:
            err = 'Please enter a jack file or directory' \
                  ' containing jack files'
            print err
            sys.exit()

    if isDirectory:
        for f in glob.glob('*.jack'):
            try:
                c = CE.CompilationEngine(f)
                c.compile_class()
            except:
                print 'An error occurred'
                for f in glob.glob('*.vm'):
                    os.remove(f)
                raise
    else:
        try:
            c = CE.CompilationEngine(fileName)
            c.compile_class()

        except:
            print 'An error occurred'
            for f in glob.glob('*.vm'):
                os.remove(f)
            raise
    return

if __name__ == "__main__":
    main()
"""
