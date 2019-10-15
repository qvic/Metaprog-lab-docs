from unittest import TestCase

from util.util import SourceFile


class TestSourceFile(TestCase):

    def test_search_for_docs(self):
        source_file = SourceFile('testdata/src/main/java/org/junit/platform/engine/TestEngine.java')
        for docstring in source_file.search_for_docs():
            print(docstring)
            print('-' * 30)
