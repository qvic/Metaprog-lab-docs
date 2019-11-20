import os
from collections import deque
from typing import List

from lexer.fmt import FiniteStateMachine
from lexer.states import InitialState
from page.generator import PageGenerator
from parser.fmt import ParserFiniteStateMachine
from parser.states import ParserInitialState
from util.util import FileTreeNode, SourceFile, Helpers, DocumentedClass, DocumentedMethod, DocumentedInterface, \
    Delimiter, PackageName, Imports, Declaration, DocumentedFile, DocumentedProperty, DocumentedEnum


class Parser:
    ACCEPTED_EXTENSIONS = ['.java']
    SCAN_DIR = 'java'

    @staticmethod
    def parse(dir_path: str):
        tree = Parser._to_package_structure(
            Parser._generate_tree_from_list(
                Parser._list_files_hierarchy(dir_path)))

        print(tree)

        tree.apply(lambda file: Parser.parse_source_file(file))

        PageGenerator.copy_resources()

        tree.traverse(lambda documented_file: PageGenerator.create_file(tree, documented_file))

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
    def _to_package_structure(tree: FileTreeNode) -> FileTreeNode:
        queue = deque()
        queue.append(tree)

        while queue:
            tree = queue.popleft()
            if tree.directory == Parser.SCAN_DIR:
                return tree.children[0]

            for subtree in tree.children:
                queue.append(subtree)

    @staticmethod
    def parse_source_file(source_file: SourceFile) -> DocumentedFile:
        contents = source_file.read_all()
        doc_file = Parser.parse_structure(contents)
        doc_file.file_path = source_file.file_path
        return doc_file

    @staticmethod
    def parse_structure(file_contents: str) -> DocumentedFile:
        fmt = FiniteStateMachine(InitialState())
        fmt.process_string(file_contents)
        partition = fmt.partition.exclude('WhitespaceState', 'InitialState')

        fmt = ParserFiniteStateMachine(ParserInitialState())
        fmt.process_tokens(partition)

        iterator = Parser.from_partition(fmt._partition)
        stack = deque()

        file = DocumentedFile()

        for obj in iterator:
            if isinstance(obj, DocumentedClass) or \
                    isinstance(obj, DocumentedInterface) or \
                    isinstance(obj, DocumentedEnum):
                file.classes.append(obj)

                if len(stack) > 0:
                    stack[-1].inner_classes.append(obj)

                stack.append(obj)

            elif isinstance(obj, DocumentedProperty):
                if len(stack) == 0:
                    raise Exception('Property is not in the class')

                if isinstance(stack[-1], DocumentedClass) or isinstance(stack[-1], DocumentedEnum):
                    stack[-1].properties.append(obj)

            elif isinstance(obj, DocumentedMethod):
                if len(stack) == 0:
                    raise Exception('Method is not in the class')

                if isinstance(stack[-1], DocumentedClass) or \
                        isinstance(stack[-1], DocumentedInterface) or \
                        isinstance(stack[-1], DocumentedEnum):

                    stack[-1].methods.append(obj)
                    if not obj.signature:
                        stack.append(obj)

            elif isinstance(obj, Delimiter) and obj.char == '}':
                try:
                    stack.pop()
                except IndexError:
                    print("Unexpected closing bracket")

            elif isinstance(obj, Delimiter) and obj.char == '{':
                stack.append(None)

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

            # class

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

            # enum

            elif state == 'EnumState':
                yield imports
                obj = DocumentedEnum.from_declaration(declaration)

            elif state == 'EnumNameState':
                obj.name = tokens[0].value

            elif state == 'EnumImplementsListState':
                obj.implements_list.extend([token.value for token in tokens[1:] if token.state != 'DelimiterState'])

            elif state == 'EnumValuesListState':
                obj.values.extend([token.value for token in tokens])

            elif state == 'EnumOpenBracketState':
                yield obj
                declaration = Declaration()

            # interface

            elif state == 'InterfaceState':
                obj = DocumentedInterface.from_declaration(declaration)

            elif state == 'InterfaceNameState':
                obj.name = tokens[0].value

            elif state == 'InterfaceExtendsListState':
                obj.extends_list.extend([token.value for token in tokens[1:] if token.state != 'DelimiterState'])

            elif state == 'InterfaceOpenBracketState':
                yield obj
                declaration = Declaration()

            elif state == 'MethodOrPropertyTypeState':
                declaration.type = tokens[0].value

            elif state == 'MethodOrPropertyNameState':
                declaration.name = tokens[0].value

            # property

            elif state == 'PropertyDelimiter':
                obj = DocumentedProperty.from_declaration(declaration)
                yield obj
                declaration = Declaration()

            # method

            elif state == 'MethodArgumentsState':
                obj = DocumentedMethod.from_declaration(declaration)
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
