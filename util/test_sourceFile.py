from unittest import TestCase

from parser.parser import Parser
from util.util import SourceFile


class TestSourceFile(TestCase):

    def test_search_for_docs(self):
        source_file = SourceFile('testdata/src/main/java/org/junit/platform/engine/TestEngine.java')
        for docstring in Parser._search_for_comments(source_file):
            print(docstring)
            print('-' * 30)
