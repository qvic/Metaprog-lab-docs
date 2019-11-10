import os
from collections import deque
from typing import List

from lexer.fmt import FiniteStateMachine
from lexer.states import InitialState
from page.generator import PageGenerator
from parser.fmt import ParserFiniteStateMachine
from parser.states import ParserInitialState
from util.util import FileTreeNode, SourceFile, Helpers, DocumentedClass, DocumentedMethod, DocumentedInterface, \
    Delimiter, PackageName, Imports, Declaration, DocumentedFile


class Parser:
    ACCEPTED_EXTENSIONS = ['.java']

    @staticmethod
    def parse(dir_path: str):
        tree = Parser._generate_tree_from_list(Parser._list_files_hierarchy(dir_path))
        print(tree)
        tree.traverse(lambda file: PageGenerator.create_file(file.file_path, Parser.parse_structure(file.read_all())))
        # tree.traverse(lambda file: Parser.parse_structure(file.read_all()))

    @staticmethod
    def _list_files_hierarchy(dir_path: str) -> List:
        result = []

        for root, dirs, files in os.walk(dir_path):
            result.append((root, dirs, files))

        return result

    @staticmethod
    def _generate_tree_from_list(file_hierarchy_list: List) -> FileTreeNode:
        if len(file_hierarchy_list) == 0:
            raise Exception('Path does not exist')

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
    def parse_structure(file_contents):
        fmt = FiniteStateMachine(InitialState())
        fmt.process_string(file_contents)
        partition = fmt.partition.exclude('WhitespaceState', 'InitialState')

        fmt = ParserFiniteStateMachine(ParserInitialState())
        fmt.process_tokens(partition)

        iterator = Parser.from_partition(fmt._partition)
        stack = deque()

        file = DocumentedFile()

        for obj in iterator:
            if isinstance(obj, DocumentedClass) or isinstance(obj, DocumentedInterface):
                file.classes.append(obj)

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

            elif isinstance(obj, Delimiter) and obj.char == '}':
                try:
                    stack.pop()
                except IndexError:
                    print("Unexpected closing bracket")

            elif isinstance(obj, Delimiter) and obj.char == '{':
                stack.append('Block')

            elif isinstance(obj, PackageName):
                file.package = obj.name

            elif isinstance(obj, Imports):
                file.imports = obj.names

        return file

    @staticmethod
    def from_partition(token_states):
        obj = None
        imports = Imports()
        package = PackageName()
        declaration = Declaration()

        for state, tokens in token_states:
            if state == 'ImportState':
                imports.add_name(tokens[1].value)

            elif state == 'PackageState':
                package.name = tokens[1].value
                yield package

            elif state == 'DeclarationWithDocsState':
                declaration.docs = tokens[0].value

            elif state == 'DeclarationWithAnnotationsState':
                declaration.annotations.extend([token.value for token in tokens])

            elif state == 'DeclarationWithAccessModifiersState':
                declaration.access_modifier = tokens[0].value

            elif state == 'DeclarationWithModifiersState':
                declaration.modifiers.extend([token.value for token in tokens])

            elif state == 'ClassState':
                yield imports
                obj = DocumentedClass.from_declaration(declaration)

            elif state == 'ClassNameState':
                obj.name = tokens[0].value

            elif state == 'ClassExtendsState':
                obj.extends = tokens[1].value

            elif state == 'ClassImplementsListState':
                obj.implements_list.extend([token.value for token in tokens[1:] if token.state != 'DelimiterState'])

            elif state == 'ClassOpenBracketState':
                yield obj
                declaration = Declaration()

            elif state == 'InterfaceState':
                obj = DocumentedInterface.from_declaration(declaration)

            elif state == 'InterfaceNameState':
                obj.name = tokens[0].value

            elif state == 'InterfaceExtendsListState':
                obj.extends_list.extend([token.value for token in tokens[1:] if token.state != 'DelimiterState'])

            elif state == 'InterfaceOpenBracketState':
                yield obj
                declaration = Declaration()

            elif state == 'MethodReturnTypeState':
                obj = DocumentedMethod.from_declaration(declaration)
                obj.return_type = tokens[0].value

            elif state == 'MethodNameState':
                obj.name = tokens[0].value

            elif state == 'MethodArgumentsState':
                obj.args = DocumentedMethod.parse_method_args(tokens[0].value)

            elif state == 'InterfaceMethodDelimiter':
                obj.signature = True
                yield obj
                declaration = Declaration()

            elif state == 'MethodOpenBracketState':
                yield obj
                declaration = Declaration()

            elif state == 'ClosedBracketState':
                yield Delimiter(tokens[0].value)

            elif state == 'OpenBracketState':
                yield Delimiter(tokens[0].value)

            elif state == 'DeadState':
                declaration = Declaration()

        return

    @staticmethod
    def trim_docstring(docs: str) -> str:
        return docs[3:-2]
