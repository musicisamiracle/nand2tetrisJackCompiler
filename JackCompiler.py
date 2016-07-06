from lxml import etree as ET
from CompilationEngine import CompilationEngine

try:
    c = CompilationEngine('Average/Main.jack')
    c.compile_class()
    print ET.tostring(c.xmlNew, pretty_print=True)
except:
    print ET.tostring(c.xmlNew, pretty_print=True)
    raise
