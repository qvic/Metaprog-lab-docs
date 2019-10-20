import os
import re
from collections import deque
from pprint import pprint
from typing import List

from fmt.fmt import FiniteStateMachine
from fmt.states import InitialState
from util.util import FileTreeNode, SourceFile, Helpers, DocumentedClass


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
    def parse_docs(file_contents):
        fmt = FiniteStateMachine(InitialState())
        fmt.process_string(file_contents)
        partition = Parser._remove_whitespaces(fmt.string_partition)

        for i, (state_type, string_value) in enumerate(partition):
            if state_type == 'IdentifierState' and string_value == 'class':
                print(Parser._detect_class(partition, i))

    @staticmethod
    def _remove_whitespaces(partition):
        return [item for item in partition if item[0] != 'WhitespaceState' and item[0] != 'InitialState']

    @staticmethod
    def _detect_class(partition, i):
        cls = DocumentedClass()

        if partition[i + 1][0] == 'NameState':
            cls.name = partition[i + 1][1]
        else:
            i += 1

        if partition[i - 1][0] == 'AccessModifierState':
            cls.access_modifier = partition[i - 1][1]
        else:
            i += 1

        while partition[i - 2][0] == 'AnnotationState':
            cls.annotations.append(partition[i - 2][1])
            i -= 1
        i += 1

        if partition[i - 3][0] == 'JavadocState':
            cls.docs = partition[i - 3][1]
        else:
            i += 1

        return cls
