from unittest import TestCase

from parser.parser import Parser


class TestPageGenerator(TestCase):
    def test_from_directory(self):
        Parser.parse('tests/testdata/Java/ciphers/AES.java', 'html/', verbose=True)
