import os
import re
from collections import deque
from typing import List

from util.util import FileTreeNode, SourceFile, Helpers


class Parser:
    ACCEPTED_EXTENSIONS = ['.java']

    @staticmethod
    def _list_files_hierarchy(dir_path: str) -> List:
        result = []

        for root, dirs, files in os.walk(dir_path):
            result.append((root, dirs, files))

        return result

    @staticmethod
    def _generate_tree_from_list(file_hierarchy_list: List) -> FileTreeNode:
        root_path, root_directories, root_files = file_hierarchy_list[0]
        root_node = FileTreeNode(root_path, root_files)

        stack = deque()
        stack.append(root_node)

        for root, dirs, files in file_hierarchy_list:
            last_node = stack.pop()

            filtered_files = filter(lambda file: Helpers.get_file_extension(file) in Parser.ACCEPTED_EXTENSIONS, files)
            last_node.files = list(map(lambda file: SourceFile(os.path.join(root, file)), filtered_files))

            for directory in reversed(dirs):
                node = FileTreeNode(directory, [])
                last_node.children.append(node)
                stack.append(node)

        return root_node

    @staticmethod
    def _search_for_comments(source_file: SourceFile):
        current_doc = ''
        signature = ''
        in_doc = False
        in_signature = False

        for line in source_file.lines():
            line = line.strip()

            if line.startswith('/**'):
                in_doc = True
            elif in_doc and line.startswith('*/'):
                in_doc = False
                # yield current_doc
                # current_doc = ''
                in_signature = True
            elif in_signature:
                m = re.split(r'[{;]', line)
                if m is not None:
                    in_signature = False
                    yield (current_doc, signature + m[0].strip())
                    current_doc = ''
                    signature = ''
                else:
                    signature += line
            elif in_doc:
                current_doc += line + '\n'
