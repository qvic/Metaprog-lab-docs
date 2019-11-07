import os
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
        self.signature = False

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    @staticmethod
    def parse_method_args(args: str):
        # todo fix generic argument with comma
        args_without_parenthesis = args[1:-1].strip()
        if len(args_without_parenthesis) == 0:
            return []
        args_with_types = args_without_parenthesis.split(',')
        return [arg.split() for arg in args_with_types]

    @staticmethod
    def create(docs, annotations, access_modifier, modifiers, return_type, name, args, signature=False):
        self = DocumentedMethod()
        self.docs = docs
        self.annotations = annotations
        self.access_modifier = access_modifier
        self.modifiers = modifiers
        self.return_type = return_type
        self.name = name
        self.args = args
        self.signature = signature
        return self


class Delimiter(Representable):

    def __init__(self, char):
        self.char = char

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False
