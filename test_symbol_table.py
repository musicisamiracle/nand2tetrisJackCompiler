import unittest
import SymbolTable


class TestSymbolTable(unittest.TestCase):

    def setUp(self):
        self.st = SymbolTable.SymbolTable()

    def tearDown(self):
        self.st = None


class SubroutineTest(TestSymbolTable):

    def test_start_subroutine(self):

        self.st.argIndex = 1
        self.st.varIndex = 2
        self.st.subDict = {'x': {'index': 0,
                                 'kind': 'STATIC',
                                 'type': 'int'}}
        self.st.start_subroutine()
        self.assertEqual(self.st.argIndex, 0)
        self.assertEqual(self.st.varIndex, 0)
        self.assertFalse(self.st.subDict)


class DefineTest(TestSymbolTable):

    def test_define(self):

        self.st.define('y', 'char', 'STATIC')
        self.st.define('z', 'int', 'FIELD')
        self.st.define('x', 'boolean', 'VAR')
        self.st.define('a', 'Box', 'ARG')

        self.assertIn('y', self.st.classDict)
        self.assertIn('z', self.st.classDict)
        self.assertIn('x', self.st.subDict)
        self.assertIn('a', self.st.subDict)


class VarCountTest(TestSymbolTable):

    def test_var_count(self):
        self.st.define('y', 'char', 'STATIC')
        self.st.define('z', 'int', 'STATIC')
        self.st.define('x', 'boolean', 'VAR')
        self.st.define('a', 'Box', 'VAR')
        self.st.define('c', 'int', 'FIELD')

        self.assertEqual(self.st.var_count('STATIC'), 2)
        self.assertEqual(self.st.var_count('VAR'), 2)
        self.assertEqual(self.st.var_count('ARG'), 0)
        self.assertEqual(self.st.var_count('FIELD'), 1)


class KindOfTest(TestSymbolTable):

    def test_kind_of(self):

        self.st.define('y', 'char', 'STATIC')
        self.st.define('z', 'int', 'FIELD')
        self.st.define('x', 'boolean', 'VAR')
        self.st.define('a', 'Box', 'ARG')

        self.assertEqual(self.st.kind_of('x'), 'VAR')
        self.assertEqual(self.st.kind_of('z'), 'FIELD')
        self.assertEqual(self.st.kind_of('y'), 'STATIC')
        self.assertEqual(self.st.kind_of('a'), 'ARG')


class TypeOfTest(TestSymbolTable):

    def test_type_of(self):

        self.st.define('y', 'char', 'STATIC')
        self.st.define('z', 'int', 'FIELD')
        self.st.define('x', 'boolean', 'VAR')
        self.st.define('a', 'Box', 'ARG')

        self.assertEqual(self.st.type_of('x'), 'boolean')
        self.assertEqual(self.st.type_of('z'), 'int')
        self.assertEqual(self.st.type_of('y'), 'char')
        self.assertEqual(self.st.type_of('a'), 'Box')


class IndexOfTest(TestSymbolTable):

    def test_index_of(self):

        self.st.define('y', 'char', 'STATIC')
        self.st.define('z', 'int', 'FIELD')
        self.st.define('x', 'boolean', 'VAR')
        self.st.define('a', 'Box', 'ARG')

        self.st.define('b', 'char', 'STATIC')
        self.st.define('c', 'int', 'FIELD')
        self.st.define('d', 'boolean', 'VAR')
        self.st.define('e', 'Box', 'ARG')

        self.assertEqual(self.st.index_of('b'), 1)
        self.assertEqual(self.st.index_of('z'), 0)
        self.assertEqual(self.st.index_of('d'), 1)
        self.assertEqual(self.st.index_of('a'), 0)

if __name__ == '__main__':
    unittest.main()
