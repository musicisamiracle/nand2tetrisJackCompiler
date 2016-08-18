import CompilationEngine as CE
import sys
import glob
import os


def main():

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
        files = glob.glob('*.jack')
        if files == []:
            err = 'Please enter a jack file or directory' \
                  ' containing jack files'
            print err
            sys.exit()

        for f in files:
            try:
                c = CE.CompilationEngine(f)
                c.compile_class()
            except:
                print 'An error occurred'
                for f in glob.glob('*.vm'):
                    os.remove(f)
                # raise

    else:
        try:
            c = CE.CompilationEngine(fileName)
            c.compile_class()

        except:
            print 'An error occurred'
            for f in glob.glob('*.vm'):
                os.remove(f)
            # raise
    return

if __name__ == "__main__":
    main()
