import os
from collections import deque
from typing import List

from util.util import FileTreeNode


class Parser:
    ACCEPTED_EXTENSIONS = ['.java']

    def _list_files_hierarchy(self, dir_path: str):
        result = []
        for root, dirs, files in os.walk(dir_path):
            result.append((root, dirs, files))
        return result

    def _generate_tree_from_list(self, file_hierarchy_list: List):
        root_path, root_directories, root_files = file_hierarchy_list[0]
        root_node = FileTreeNode(root_path, root_files)

        stack = deque()
        stack.append(root_node)

        for root, dirs, files in file_hierarchy_list:
            last_node = stack.pop()

            print(root)
            print(files)
            filtered_files = filter(lambda file: os.path.splitext(file)[1] in self.ACCEPTED_EXTENSIONS, files)
            last_node.files = list(map(lambda file: os.path.join(root, file), filtered_files))

            for directory in reversed(dirs):
                node = FileTreeNode(directory, [])
                last_node.children.append(node)
                stack.append(node)

        return root_node
