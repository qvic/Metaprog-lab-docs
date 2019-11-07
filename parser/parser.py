import os
from collections import deque
from pprint import pprint
from typing import List

from lexer.fmt import FiniteStateMachine
from lexer.states import InitialState
from lexer.util import LexerPartition
from parser.fmt import ParserFiniteStateMachine
from parser.states import ParserInitialState
from util.util import FileTreeNode, SourceFile, Helpers, DocumentedClass, DocumentedMethod, DocumentedInterface, \
    Delimiter


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

        fmt = ParserFiniteStateMachine(ParserInitialState())
        fmt.process_tokens(partition)

        iterator = Parser.from_partition(fmt._partition)

        for obj in iterator:
            if isinstance(obj, DocumentedClass) or isinstance(obj, DocumentedInterface):
                # todo skip parsed tokens
                classes.append(obj)

                if len(stack) > 0:
                    stack[-1].inner_classes.append(obj)

                stack.append(obj)

            elif isinstance(obj, DocumentedMethod):
                if len(stack) == 0:
                    raise Exception('Method is not in the class')

                if isinstance(stack[-1], DocumentedClass) or isinstance(stack[-1], DocumentedInterface):
                    stack[-1].methods.append(obj)
                    if not obj.signature:
                        stack.append(obj)

            elif isinstance(obj, Delimiter) and obj.char == '}':  # todo is closing bracket helper method
                try:
                    stack.pop()
                except IndexError:
                    print("Unexpected closing bracket")
            elif isinstance(obj, Delimiter) and obj.char == '{':
                stack.append('Block')

        return classes

    @staticmethod
    def from_partition(token_states):
        obj = None
        map = {'docs': None, 'annotations': [], 'access_modifier': None, 'modifiers': [], 'implements': [],
               'extends': None}

        for state, tokens in token_states:
            if state == 'DeclarationWithDocsState':
                map['docs'] = tokens[0].value

            elif state == 'DeclarationWithAnnotationsState':
                map['annotations'].extend([token.value for token in tokens])

            elif state == 'DeclarationWithAccessModifiersState':
                map['access_modifier'] = tokens[0].value

            elif state == 'DeclarationWithModifiersState':
                map['modifiers'].extend([token.value for token in tokens])

            elif state == 'ClassState':
                obj = DocumentedClass()
                obj.docs = map['docs']
                obj.annotations = map['annotations']
                obj.access_modifier = map['access_modifier']
                obj.modifiers = map['modifiers']

            elif state == 'ClassNameState':
                obj.name = tokens[0].value

            elif state == 'ClassExtendsState':
                obj.extends = tokens[1].value

            elif state == 'ClassImplementsListState':
                obj.implements_list.extend([token.value for token in tokens[1:] if token.state != 'DelimiterState'])

            elif state == 'ClassOpenBracketState':
                yield obj
                # todo don't reassign, create new class for this purpose
                map = {'docs': None, 'annotations': [], 'access_modifier': 'package-private', 'modifiers': [],
                       'implements': [],
                       'extends': None}

            elif state == 'InterfaceState':
                obj = DocumentedInterface()
                obj.docs = map['docs']
                obj.annotations = map['annotations']
                obj.access_modifier = map['access_modifier']
                obj.modifiers = map['modifiers']

            elif state == 'InterfaceNameState':
                obj.name = tokens[0].value

            elif state == 'InterfaceExtendsListState':
                obj.extends_list.extend([token.value for token in tokens[1:] if token.state != 'DelimiterState'])

            elif state == 'InterfaceOpenBracketState':
                yield obj
                map = {'docs': None, 'annotations': [], 'access_modifier': 'package-private', 'modifiers': [],
                       'implements': [],
                       'extends': None}

            elif state == 'MethodReturnTypeState':
                obj = DocumentedMethod()
                obj.return_type = tokens[0].value
                obj.docs = map['docs']
                obj.annotations = map['annotations']
                obj.access_modifier = map['access_modifier']
                obj.modifiers = map['modifiers']

            elif state == 'MethodNameState':
                obj.name = tokens[0].value

            elif state == 'MethodArgumentsState':
                obj.args = DocumentedMethod.parse_method_args(tokens[0].value)

            elif state == 'InterfaceMethodDelimiter':
                obj.signature = True
                yield obj
                map = {'docs': None, 'annotations': [], 'access_modifier': 'package-private', 'modifiers': [],
                       'implements': [],
                       'extends': None}

            elif state == 'MethodOpenBracketState':
                yield obj
                map = {'docs': None, 'annotations': [], 'access_modifier': 'package-private', 'modifiers': [],
                       'implements': [],
                       'extends': None}

            elif state == 'ClosedBracketState':
                yield Delimiter(tokens[0].value)

            elif state == 'OpenBracketState':
                yield Delimiter(tokens[0].value)

            elif state == 'DeadState':
                map = {'docs': None, 'annotations': [], 'access_modifier': 'package-private', 'modifiers': [],
                       'implements': [],
                       'extends': None}

        return
