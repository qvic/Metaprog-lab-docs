import os
from collections import Counter
from pprint import pprint
from typing import List


class Helpers:

    @staticmethod
    def get_file_extension(file_path):
        return os.path.splitext(file_path)[1]


class Representable:

    def __repr__(self) -> str:
        return '{}[{}]'.format(type(self).__name__, ', '.join('%s=%s' % item for item in vars(self).items()))


class FileTreeNode:

    def __init__(self, directory: str, files: List, children: List = None):
        if children is None:
            children = []

        self.files = files
        self.directory = directory
        self.children = children

    def __eq__(self, o: object) -> bool:
        if isinstance(o, FileTreeNode):
            fields_equal = o.directory == self.directory and set(o.files) == set(self.files)

            if not fields_equal:
                return False

            if self.children == [] and o.children == []:
                return fields_equal

            children = sorted(self.children, key=lambda node: node.directory)
            objects_children = sorted(o.children, key=lambda node: node.directory)

            for n1, n2 in zip(children, objects_children):
                if n1 != n2:
                    return False

            return fields_equal

        return False

    def __repr__(self, level=0) -> str:
        result = "\t" * level + str(self.directory) + " # " + str(list(self.files)) + "\n"

        for child in self.children:
            result += child.__repr__(level + 1)

        return result


class SourceFile(Representable):

    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_all(self):
        with open(self.file_path, 'r') as file:
            return file.read()

    def __eq__(self, o: object) -> bool:
        if isinstance(o, SourceFile):
            return self.file_path == o.file_path
        return False

    def __hash__(self) -> int:
        return hash(self.file_path)


class DocumentedClass(Representable):

    def __init__(self):
        self.docs = None
        self.annotations = []
        self.access_modifier = 'package-private'
        self.modifiers = []
        self.name = None
        self.extends = None
        self.implements_list = []
        self.methods = []
        self.inner_classes = []

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    @staticmethod
    def from_tokens(before_class_keyword, after_class_keyword):
        self = DocumentedClass()
        self.name = after_class_keyword[0].value

        has_extends = False
        has_implements = False
        for token in after_class_keyword:
            if token.state == 'IdentifierState':
                if token.value == 'extends':
                    has_extends = True
                elif token.value == 'implements':
                    has_implements = True
            elif token.state == 'NameState':
                if has_extends:
                    self.extends = token.value
                    has_extends = False
                elif has_implements:
                    self.implements_list.append(token.value)

        for token in before_class_keyword:
            if token.state == 'JavadocState':
                self.docs = token.value
            elif token.state == 'AnnotationState':
                self.annotations.append(token.value)
            elif token.state == 'AccessModifierState':
                self.access_modifier = token.value or self.access_modifier
            elif token.state == 'ModifierState':
                self.modifiers.append(token.value)
        return self

    @staticmethod
    def create(docs, annotations, access_modifier, modifiers, name, extends, implements_list, methods, inner_classes):
        self = DocumentedClass()
        self.docs = docs
        self.annotations = annotations
        self.access_modifier = access_modifier
        self.modifiers = modifiers
        self.name = name
        self.extends = extends
        self.implements_list = implements_list
        self.inner_classes = inner_classes
        self.methods = methods
        return self


class DocumentedInterface(Representable):

    def __init__(self):
        self.docs = None
        self.annotations = []
        self.access_modifier = 'package-private'
        self.modifiers = []
        self.name = None
        self.extends_list = []
        self.methods = []
        self.inner_classes = []

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    @staticmethod
    def create(docs, annotations, access_modifier, modifiers, name, extends_list, methods, inner_classes):
        self = DocumentedInterface()
        self.docs = docs
        self.annotations = annotations
        self.access_modifier = access_modifier
        self.modifiers = modifiers
        self.name = name
        self.extends_list = extends_list
        self.methods = methods
        self.inner_classes = inner_classes
        return self


class DocumentedMethod(Representable):

    def __init__(self):
        # todo static and final
        self.docs = None
        self.annotations = []
        self.access_modifier = 'package-private'
        self.modifiers = []
        self.return_type = None
        self.name = None
        self.args = []

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    @staticmethod
    def parse_method_args(args: str):
        args_without_parenthesis = args[1:-1].strip()
        if len(args_without_parenthesis) == 0:
            return []
        args_with_types = args_without_parenthesis.split(',')
        return [arg.split() for arg in args_with_types]

    @staticmethod
    def create(docs, annotations, access_modifier, modifiers, return_type, name, args):
        self = DocumentedMethod()
        self.docs = docs
        self.annotations = annotations
        self.access_modifier = access_modifier
        self.modifiers = modifiers
        self.return_type = return_type
        self.name = name
        self.args = args
        return self
