class FileTreeNode:

    def __init__(self, directory, files, children=None):
        if children is None:
            children = []

        self.files = files
        self.directory = directory
        self.children = children

    def __repr__(self, level=0):
        result = "\t" * level + str(self.directory) + " # " + str(list(self.files)) + "\n"

        for child in self.children:
            result += child.__repr__(level + 1)

        return result


class SourceFile:

    def __init__(self, file_path):
        self.file_path = file_path
