from unittest import TestCase

from util.util import DocumentedFile


class TestDocumentedFile(TestCase):

    def test_get_import_path_1(self):
        file = DocumentedFile()
        file.package = 'org.test.package.core.x'
        file.imports = ['org.test.package.Kek', 'org.test.package.Class']

        file_list = [DocumentedFile()]
        file_list[0].package = 'org.test.package'
        file_list[0].file_path = 'org/test/package/Class.java'

        self.assertEqual(file.get_doc_import_path('Class', file_list), '../../Class.java.html')

    def test_get_import_path_2(self):
        file = DocumentedFile()
        file.package = 'org.test.package'
        file.imports = ['org.test.package.Kek', 'org.test.package.core.Class']

        file_list = [DocumentedFile()]
        file_list[0].package = 'org.test.package.core'
        file_list[0].file_path = 'org/test/package/core/Class.java'

        self.assertEqual(file.get_doc_import_path('Class', file_list), 'core/Class.java.html')

    def test_get_import_path_disjoint(self):
        file = DocumentedFile()
        file.package = 'org.test.package'
        file.imports = ['java.util.JavaClass', 'org.test.Class']

        # or return link to online java doc
        self.assertEqual(file.get_doc_import_path('JavaClass', []), None)
