import os
from collections import deque
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

    def traverse(self, callback):
        queue = deque()
        queue.append(self)

        while queue:
            tree = queue.popleft()
            for file in tree.files:
                callback(file)

            for subtree in tree.children:
                queue.append(subtree)

    def apply(self, function, verbose):
        queue = deque()
        queue.append(self)

        while queue:
            tree = queue.popleft()
            for i, file in enumerate(tree.files):
                tree.files[i] = function(file)
                if verbose:
                    print('read', file.file_path)

            for subtree in tree.children:
                queue.append(subtree)


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


class DocumentedEnum(Representable):

    def __init__(self):
        self.docs = None
        self.annotations = []
        self.access_modifier = None
        self.modifiers = []
        self.name = None
        self.extends = None
        self.implements_list = []
        self.methods = []
        self.inner_classes = []
        self.properties = []
        self.values = []

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    @staticmethod
    def from_declaration(declaration: 'Declaration') -> 'DocumentedEnum':
        self = DocumentedEnum()
        self.docs = declaration.docs
        self.annotations = declaration.annotations
        self.access_modifier = declaration.access_modifier
        self.modifiers = declaration.modifiers
        return self


class EnumValue(Representable):

    def __init__(self, value):
        self.value = value


class DocumentedClass(Representable):

    def __init__(self):
        self.docs = None
        self.annotations = []
        self.access_modifier = None
        self.modifiers = []
        self.name = None
        self.extends = None
        self.implements_list = []
        self.methods = []
        self.inner_classes = []
        self.properties = []

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    @staticmethod
    def create(docs, annotations, access_modifier, modifiers, name, extends, implements_list, methods,
               inner_classes) -> 'DocumentedClass':
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

    @staticmethod
    def from_declaration(declaration: 'Declaration') -> 'DocumentedClass':
        self = DocumentedClass()
        self.docs = declaration.docs
        self.annotations = declaration.annotations
        self.access_modifier = declaration.access_modifier
        self.modifiers = declaration.modifiers
        return self


class DocumentedInterface(Representable):

    def __init__(self):
        self.docs = None
        self.annotations = []
        self.access_modifier = None
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
    def create(docs, annotations, access_modifier, modifiers, name, extends_list, methods,
               inner_classes) -> 'DocumentedInterface':
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

    @staticmethod
    def from_declaration(declaration: 'Declaration') -> 'DocumentedInterface':
        self = DocumentedInterface()
        self.docs = declaration.docs
        self.annotations = declaration.annotations
        self.access_modifier = declaration.access_modifier
        self.modifiers = declaration.modifiers
        return self


class DocumentedMethod(Representable):

    def __init__(self):
        self.docs = None
        self.annotations = []
        self.access_modifier = 'package-private'
        self.modifiers = []
        self.return_type = None
        self.name = None
        self.args = []
        self.signature = False
        self.post_args = None
        self.throws = []

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
    def create(docs, annotations, access_modifier, modifiers, return_type, name, args,
               signature=False) -> 'DocumentedMethod':
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

    @staticmethod
    def from_declaration(declaration: 'Declaration') -> 'DocumentedMethod':
        self = DocumentedMethod()
        self.docs = declaration.docs
        self.annotations = declaration.annotations
        self.access_modifier = declaration.access_modifier or self.access_modifier
        self.modifiers = declaration.modifiers
        self.return_type = declaration.type
        self.name = declaration.name
        return self


class DocumentedProperty(Representable):

    def __init__(self):
        self.docs = None
        self.annotations = []
        self.access_modifier = 'package-private'
        self.modifiers = []
        self.type = None
        self.name = None

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    @staticmethod
    def from_declaration(declaration: 'Declaration') -> 'DocumentedProperty':
        self = DocumentedProperty()
        self.docs = declaration.docs
        self.annotations = declaration.annotations
        self.access_modifier = declaration.access_modifier or self.access_modifier
        self.modifiers = declaration.modifiers
        self.name = declaration.name
        self.type = declaration.type
        return self

    @staticmethod
    def create(docs, annotations, access_modifier, modifiers, type, name) -> 'DocumentedProperty':
        self = DocumentedProperty()
        self.docs = docs
        self.annotations = annotations
        self.access_modifier = access_modifier
        self.modifiers = modifiers
        self.type = type
        self.name = name
        return self


class Delimiter(Representable):

    def __init__(self, char):
        self.char = char

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False


class Imports(Representable):

    def __init__(self):
        self.names = []

    def add_name(self, name: str):
        self.names.append(name)


class PackageName(Representable):

    def __init__(self):
        self.name = None


class MultilineComment(Representable):

    def __init__(self, value):
        self.value = value


class Declaration(Representable):

    def __init__(self):
        self.docs = None
        self.annotations = []
        self.access_modifier = None
        self.modifiers = []
        self.type = None
        self.name = None


class DocumentedFile(Representable):

    def __init__(self):
        self.file_path = None
        self.classes = []
        self.imports = []
        self.package = None
        self.file_doc = None

    def get_file_name(self):
        return self.get_full_file_name().split('.')[0]

    def get_full_file_name(self):
        return self.file_path.split('/')[-1]

    def get_package_path(self):
        if self.package is None:
            return self.get_full_file_name()

        return os.path.join(*self.package.split('.'), self.get_full_file_name())

    def get_import_name(self):
        return self.package + '.' + self.get_file_name()

    def get_doc_import_path(self, class_name: str, file_list):
        import_names = map(lambda f: f.get_import_name(), file_list)
        for import_path in self.imports:

            splitted_path = import_path.split('.')
            if splitted_path[-1] == class_name:

                if import_path not in import_names:
                    return None

                import_path = os.path.join(*splitted_path)
                package_path = os.path.join(*self.package.split('.'))

                return os.path.relpath(import_path, package_path) + '.java.html'
        return None
