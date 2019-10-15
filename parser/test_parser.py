from unittest import TestCase

from parser.parser import Parser
from util.util import FileTreeNode


class TestParser(TestCase):

    def setUp(self):
        self.parser = Parser()

    def test_list_files_hierarchy(self):
        print(self.parser._list_files_hierarchy("testdata"))

    def test_generate_tree_from_list(self):
        """
        a/b/f1.java
        a/b/c/f2.java
        a/b/c/f3.java
        a/b/d/f4.java

        to

        a -> b -> [c -> [f2.java, f3.java], d -> [f4.java], f1.java]
        :return:
        """

        tree = self.parser._generate_tree_from_list(
            [('a', ['b'], []),
             ('b', ['c', 'd'], ['f1.java']),
             ('c', [], ['f2.java', 'f3.java']),
             ('d', [], ['f4.java'])])

        print(tree)
