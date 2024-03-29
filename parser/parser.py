import os
from collections import deque
from typing import List

from lexer.fmt import FiniteStateMachine
from lexer.states import InitialState
from page.generator import PageGenerator
from parser.fmt import ParserFiniteStateMachine
from parser.states import ParserInitialState
from util.util import FileTreeNode, SourceFile, Helpers, DocumentedClass, DocumentedMethod, DocumentedInterface, \
    Delimiter, PackageName, Imports, Declaration, DocumentedFile, DocumentedProperty, DocumentedEnum, EnumValue, \
    MultilineComment


class Parser:
    ACCEPTED_EXTENSIONS = ['.java']

    @staticmethod
    def parse(input_path: str, output_dir: str, project_name: str = None, project_version: str = None,
              verbose: bool = False, shallow: bool = False):

        if project_name is None:
            project_name = input_path

        if os.path.isfile(input_path):
            tree = Parser._generate_tree_from_list([(os.path.dirname(input_path), [], [os.path.basename(input_path)])])
        elif os.path.isdir(input_path):
            tree = Parser._generate_tree_from_list(Parser._list_files_hierarchy(input_path, shallow))
        else:
            raise ValueError('Invalid input path.')

        if verbose:
            print("Project file structure:")
            print(tree)
            print()

        root_path = tree.directory
        tree.apply(lambda file: Parser.parse_source_file(file, root_path), verbose)

        PageGenerator.copy_resources(output_dir)

        file_list = []
        tree.traverse(lambda documented_file: file_list.append(documented_file))

        tree.traverse(lambda documented_file: PageGenerator.create_file(tree, documented_file, file_list, output_dir))
        PageGenerator.create_index_page(tree, file_list, project_name, project_version, output_dir)

    @staticmethod
    def _list_files_hierarchy(dir_path: str, shallow: bool) -> List:
        result = []

        for root, dirs, files in os.walk(dir_path):
            if shallow:
                result.append((root, [], files))
                break

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
    def parse_source_file(source_file: SourceFile, root_path: str) -> DocumentedFile:
        contents = source_file.read_all()
        doc_file = Parser.parse_structure(contents)

        rel_file_path = os.path.relpath(source_file.file_path, root_path)
        doc_file.file_path = rel_file_path
        return doc_file

    @staticmethod
    def parse_structure(file_contents: str) -> DocumentedFile:
        fmt = FiniteStateMachine(InitialState())
        fmt.process_string(file_contents)

        partition = fmt.partition.exclude('WhitespaceState', 'InitialState')

        parser_fmt = ParserFiniteStateMachine(ParserInitialState())
        parser_fmt.process_tokens(partition)

        iterator = Parser.generate_data_objects(parser_fmt.partition)

        stack = deque()

        file = DocumentedFile()

        for obj in iterator:
            if isinstance(obj, MultilineComment):
                if len(stack) == 0 and file.file_doc is None:
                    file.file_doc = obj.value

            elif isinstance(obj, DocumentedClass) or \
                    isinstance(obj, DocumentedInterface) or \
                    isinstance(obj, DocumentedEnum):
                if len(stack) > 0:
                    stack[-1].inner_classes.append(obj)
                else:
                    file.classes.append(obj)

                stack.append(obj)

            elif isinstance(obj, DocumentedProperty):
                if len(stack) == 0:
                    continue

                if isinstance(stack[-1], DocumentedClass) or isinstance(stack[-1], DocumentedEnum):
                    stack[-1].properties.append(obj)

            elif isinstance(obj, DocumentedMethod):
                if len(stack) == 0:
                    continue

                if isinstance(stack[-1], DocumentedClass) or \
                        isinstance(stack[-1], DocumentedInterface) or \
                        isinstance(stack[-1], DocumentedEnum):
                    stack[-1].methods.append(obj)

                if not obj.signature:
                    stack.append(obj)

            elif isinstance(obj, EnumValue):
                if len(stack) == 0:
                    continue

                if isinstance(stack[-1], DocumentedEnum):
                    stack[-1].values.append(obj.value)

            elif isinstance(obj, Delimiter) and obj.char == '}':
                try:
                    stack.pop()
                except IndexError:
                    continue

            elif isinstance(obj, Delimiter) and obj.char == '{':
                stack.append(None)

            elif isinstance(obj, PackageName):
                file.package = obj.name

            elif isinstance(obj, Imports):
                file.imports.extend(obj.names)

        return file

    @staticmethod
    def generate_data_objects(token_states):
        obj = None
        imports = Imports()
        package = PackageName()
        declaration = Declaration()

        for state, tokens in token_states:
            if state == 'ImportState':
                if len(tokens) > 1:
                    imports.add_name(tokens[1].value)

            elif state == 'PackageState':
                if len(tokens) > 1:
                    package.name = tokens[1].value
                    yield package
                    package = PackageName()

            elif state == 'DeclarationWithDocsState':
                declaration.docs = tokens[0].value

            elif state == 'DeclarationWithAnnotationsState':
                declaration.annotations.extend([token.value for token in tokens])

            elif state == 'DeclarationWithAccessModifiersState':
                declaration.access_modifier = tokens[0].value

            elif state == 'DeclarationWithModifiersState':
                declaration.modifiers.extend([token.value for token in tokens])

            elif state == 'MultilineCommentState':
                yield MultilineComment(tokens[0].value)

            # class

            elif state == 'ClassState':
                yield imports
                imports = Imports()
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
                imports = Imports()
                obj = DocumentedEnum.from_declaration(declaration)

            elif state == 'EnumNameState':
                obj.name = tokens[0].value

            elif state == 'EnumImplementsListState':
                obj.implements_list.extend([token.value for token in tokens[1:] if token.state != 'DelimiterState'])

            elif state == 'EnumValuesListState':
                yield from (EnumValue(token.value) for token in tokens)

            elif state == 'EnumOpenBracketState':
                yield obj
                declaration = Declaration()

            # interface

            elif state == 'InterfaceState':
                yield imports
                imports = Imports()
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

            elif state == 'MethodPostArgumentsState':
                obj.post_args = tokens
                if tokens[0].value == 'throws':
                    obj.throws = [token.value for token in tokens[1:] if token.state != 'DelimiterState']

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
