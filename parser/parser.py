import os
import re
from collections import deque
from typing import List

from fmt.fmt import FiniteStateMachine
from fmt.states import InitialState
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
    def parse_docs(file_content):
        fmt = FiniteStateMachine(InitialState())
