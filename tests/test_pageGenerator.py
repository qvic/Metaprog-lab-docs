from unittest import TestCase

from page.generator import PageGenerator
from parser.parser import Parser


class TestPageGenerator(TestCase):
    def test_from_directory(self):
        Parser.parse('tests/testdata/1')
