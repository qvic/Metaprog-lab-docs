from unittest import TestCase

from util.util import DocumentedFile


class TestDocumentedFile(TestCase):

    def test_get_import_path_1(self):
        file = DocumentedFile()
        file.package = 'org.test.package.core.x'
        file.imports = ['org.test.package.Kek', 'org.test.package.Class']

        self.assertEqual(file.get_doc_import_path('Class'), '../../Class.java.html')

    def test_get_import_path_2(self):
        file = DocumentedFile()
        file.package = 'org.test.package'
        file.imports = ['org.test.package.Kek', 'org.test.package.core.Class']

        self.assertEqual(file.get_doc_import_path('Class'), 'core/Class.java.html')

    def test_get_import_path_disjoint(self):
        file = DocumentedFile()
        file.package = 'org.test.package'
        file.imports = ['java.util.JavaClass', 'org.test.Class']

        # or return link to online java doc
        self.assertEqual(file.get_doc_import_path('JavaClass'), '#')
