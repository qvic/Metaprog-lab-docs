import os
from collections import deque
from pprint import pprint
from typing import List

from fmt.fmt import FiniteStateMachine
from fmt.states import InitialState
from util.util import FileTreeNode, SourceFile, Helpers, DocumentedClass, DocumentedMethod


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

        last_object = None
        classes = []
        stack = deque()
        for i, (state_type, string_value) in enumerate(partition):
            if Parser._is_class(partition, i):
                last_object = Parser._detect_class(partition, i)
                classes.append(last_object)

                if len(stack) > 0:
                    stack[-1].inner_classes.append(last_object)

            elif Parser._is_method(partition, i):
                method = Parser._detect_method(partition, i)
                last_object = method

                if len(stack) == 0:
                    raise Exception('Method is not in the class')

                stack[-1].methods.append(method)

            elif state_type == 'OpenBracketState':
                stack.append(last_object)
                # print('Entering', stack[-1])

            elif state_type == 'ClosedBracketState':
                item = stack.pop()
                # print('Leaving', item)

        return classes

    @staticmethod
    def _remove_whitespaces(partition):
        return [item for item in partition if item[0] != 'WhitespaceState' and item[0] != 'InitialState']

    @staticmethod
    def _is_method(partition, location):
        return partition[location][0] == 'NameState' and \
               partition[location + 1][0] == 'NameState' and \
               partition[location + 2][0] == 'ArgumentsParenthesisState' and \
               partition[location + 3][0] == 'OpenBracketState'

    @staticmethod
    def _detect_method(partition, location):
        method = DocumentedMethod()
        i = location

        if partition[i - 1][0] == 'AccessModifierState':
            method.access_modifier = partition[i - 1][1]
        else:
            method.access_modifier = 'package-private'

        method.return_type = partition[i][1]
        method.name = partition[i + 1][1]
        method.args = Parser._parse_method_args(partition[i + 2][1])

        while partition[i - 2][0] == 'AnnotationState':
            method.annotations.append(partition[i - 2][1])
            i -= 1
        i += 1

        if partition[i - 3][0] == 'JavadocState':
            method.docs = partition[i - 3][1]
        else:
            i += 1

        return method

    @staticmethod
    def _parse_method_args(args: str):
        args_without_parenthesis = args[1:-1].strip()
        if len(args_without_parenthesis) == 0:
            return []
        args_with_types = args_without_parenthesis.split(',')
        return [arg.split() for arg in args_with_types]

    @staticmethod
    def _is_class(partition, location):
        return partition[location][0] == 'IdentifierState' and partition[location][1] == 'class'

    @staticmethod
    def _detect_class(partition, class_token_location):
        cls = DocumentedClass()
        i = class_token_location

        if partition[i + 1][0] == 'NameState':
            cls.name = partition[i + 1][1]
        else:
            raise Exception('Class has no name')

        if partition[i + 2][0] == 'IdentifierState' and partition[i + 2][1] == 'extends':
            if partition[i + 3][0] == 'NameState':
                cls.extends = partition[i + 3][1]
            else:
                raise Exception('Class extends nothing')
        else:
            i -= 2

        if partition[i + 4][0] == 'IdentifierState' and partition[i + 4][1] == 'implements':
            if partition[i + 5][0] != 'NameState':
                raise Exception('Class implements nothing')

            k = 0
            while partition[i + 5 + k][0] == 'NameState':
                cls.implements_list.append(partition[i + 5 + k][1])
                if partition[i + 6 + k][0] == 'DelimiterState' and partition[i + 6 + k][1] == ',':
                    k += 2
                else:
                    break

        i = class_token_location

        if partition[i - 1][0] == 'AccessModifierState':
            cls.access_modifier = partition[i - 1][1]
        else:
            cls.access_modifier = 'package-private'
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
