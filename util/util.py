import os
from collections import Counter
from typing import List


class Helpers:

    @staticmethod
    def get_file_extension(file_path):
        return os.path.splitext(file_path)[1]


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


class SourceFile:

    def __init__(self, file_path: str):
        self.file_path = file_path

    def lines(self):
        with open(self.file_path, 'r') as file:
            return file.readlines()

    def __repr__(self) -> str:
        return 'SourceFile[' + self.file_path + ']'

    def __eq__(self, o: object) -> bool:
        if isinstance(o, SourceFile):
            return self.file_path == o.file_path
        return False

    def __hash__(self) -> int:
        return hash(self.file_path)


class Signature:

    def __init__(self, annotations: List, access_modifier: str, name: str):
        self.annotations = annotations
        self.access_modifier = access_modifier
        self.name = []


class ClassSignature(Signature):

    def __init__(self, annotations, access_modifier, name, extends_list):
        super().__init__(annotations, access_modifier, name)


class MethodSignature(Signature):

    def __init__(self, annotations, access_modifier, return_type, name):
        super().__init__(annotations, access_modifier, name)