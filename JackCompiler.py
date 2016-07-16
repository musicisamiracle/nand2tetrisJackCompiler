from lxml import etree as ET
from CompilationEngine import CompilationEngine

"""Need to change access to class variables into class methods"""

try:
    c = CompilationEngine('Seven/Main.jack')
    c.compile_class()
    print ET.tostring(c.xmlNew, pretty_print=True)
    print c.vm.debugOut
except:
    print ET.tostring(c.xmlNew, pretty_print=True)
    raise
