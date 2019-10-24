from unittest import TestCase

from parser.parser import Parser

def _traverse_tree(tree):
    for file in tree.files:
        print('#'*30)
        print('reading', file.file_path)
        print()
        print(Parser.parse_docs(file.read_all()))

    for child in tree.children:
        _traverse_tree(child)


class Test(TestCase):

    def test_parse_files(self):
        tree = Parser._generate_tree_from_list(Parser._list_files_hierarchy("testdata"))
        print(tree)
        _traverse_tree(tree)

