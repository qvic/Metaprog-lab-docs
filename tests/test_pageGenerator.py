from unittest import TestCase

from page_generator.generator import PageGenerator


class TestPageGenerator(TestCase):
    def test_from_directory(self):
        # pass
        PageGenerator.from_directory('testdata')
