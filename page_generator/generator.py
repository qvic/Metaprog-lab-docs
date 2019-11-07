import html
import html
import os
from pprint import pformat

from parser.parser import Parser


def _traverse_tree(tree):
    for file in tree.files:
        print('#' * 30)
        print('reading', file.file_path)
        print()
        # print(Parser.parse_docs(file.read_all()))
        # if file.file_path == 'testdata/java/util/Arrays/Sorting.java':
        PageGenerator.create_file(file.file_path, Parser.parse_docs(file.read_all()))

    for child in tree.children:
        _traverse_tree(child)


class PageGenerator:
    DIR = 'html'

    @staticmethod
    def from_directory(directory_path):
        tree = Parser._generate_tree_from_list(Parser._list_files_hierarchy(directory_path))
        print(tree)
        _traverse_tree(tree)

    @staticmethod
    def create_file(file_path, classes):
        html_file_path = os.path.join(PageGenerator.DIR, file_path + '.html')
        os.makedirs(os.path.dirname(html_file_path), exist_ok=True)

        with open(html_file_path, 'w') as file:
            file.write('<h3>' + file_path + '</h3>\n')
            file.write('<span style="white-space: pre-line">')
            str = pformat(classes, indent=4, width=80)
            file.write(html.escape(str))
            file.write('</span>')
