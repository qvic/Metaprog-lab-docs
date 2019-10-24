import os
from collections import deque
from pprint import pprint
from typing import List

from fmt.fmt import FiniteStateMachine
from fmt.states import InitialState
from fmt.util import Partition
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

        partition = fmt.partition.exclude('WhitespaceState', 'InitialState')

        classes = []
        stack = deque()

        for i, token in enumerate(partition.sequence):
            if Parser._is_class_at_index(i, partition):
                cls = Parser._detect_class(partition, i)
                # todo skip parsed tokens
                classes.append(cls)

                if len(stack) > 0:
                    stack[-1].inner_classes.append(cls)

                stack.append(cls)

            elif Parser._is_method_at_index(i, partition):
                method = Parser._detect_method(partition, i)

                if len(stack) == 0:
                    raise Exception('Method is not in the class')

                stack[-1].methods.append(method)
                stack.append(method)

            elif token.state == 'ClosedBracketState':
                try:
                    stack.pop()
                except IndexError:
                    print("unexpected closing bracket")

        return classes

    @staticmethod
    def _is_method_at_index(index: int, partition: Partition):
        return partition.state_at(index) == 'NameState' and \
               partition.state_at(index + 1) == 'NameState' and \
               partition.state_at(index + 2) == 'ArgumentsParenthesisState' and \
               partition.state_at(index + 3) == 'OpenBracketState'

    @staticmethod
    def _detect_method(partition: Partition, i: int):
        method = DocumentedMethod()

        method.return_type = partition.value_at(i)
        method.name = partition.value_at(i + 1)
        method.args = DocumentedMethod.parse_method_args(partition.value_at(i + 2))

        while partition.state_at(i - 1) == 'ModifierState':
            method.modifiers.append(partition.value_at(i - 1))
            i -= 1
        method.modifiers.reverse()
        i += 1

        if partition.state_at(i - 2) == 'AccessModifierState':
            method.access_modifier = partition.value_at(i - 2)
        else:
            method.access_modifier = 'package-private'

        while partition.state_at(i - 3) == 'AnnotationState':
            method.annotations.append(partition.value_at(i - 3))
            i -= 1
        method.annotations.reverse()
        i += 1

        if partition.state_at(i - 4) == 'JavadocState':
            method.docs = partition.value_at(i - 4)
        else:
            i += 1

        return method

    @staticmethod
    def _is_class_at_index(index: int, partition: Partition):
        return partition.state_at(index) == 'IdentifierState' \
               and partition.value_at(index) == 'class'

    @staticmethod
    def _detect_class(partition: Partition, class_token_location: int):
        tokens_after_class_keyword = []
        i = class_token_location + 1
        while partition.state_at(i) is not None:
            if partition.state_at(i) == 'OpenBracketState':
                break
            tokens_after_class_keyword.append(partition.token_at(i))
            i += 1

        tokens_before_class_keyword = []
        i = class_token_location - 1

        while partition.state_at(i) == 'ModifierState':
            tokens_before_class_keyword.append(partition.token_at(i))
            i -= 1
        i += 1

        if partition.state_at(i - 1) == 'AccessModifierState':
            tokens_before_class_keyword.append(partition.token_at(i - 1))
        else:
            i += 1

        while partition.state_at(i - 2) == 'AnnotationState':
            tokens_before_class_keyword.append(partition.token_at(i - 2))
            i -= 1
        i += 1

        if partition.state_at(i - 3) == 'JavadocState':
            tokens_before_class_keyword.append(partition.token_at(i - 3))
        else:
            i += 1

        return DocumentedClass.from_tokens(reversed(tokens_before_class_keyword), tokens_after_class_keyword)
