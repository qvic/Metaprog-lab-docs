from pprint import pprint
from unittest import TestCase

from parser.parser import Parser
from util.util import FileTreeNode, SourceFile


class TestParser(TestCase):

    def setUp(self):
        self.parser = Parser()

    # def test_list_files_hierarchy(self):
    #     print(self.parser._list_files_hierarchy("testdata"))

    def test_generate_tree_from_list(self):
        """
        a/b/f1.java
        a/b/c/f2.java
        a/b/c/f3.java
        a/b/d/f4.java

        to

        a -> b -> [c -> [f2.java, f3.java], d -> [f4.java], f1.java]
        :return:
        """

        # print(self.parser._generate_tree_from_list(self.parser._list_files_hierarchy("testdata")))

        tree = self.parser._generate_tree_from_list(
            [('a', ['b'], []),
             ('a/b', ['c', 'd'], ['f1.java']),
             ('a/b/c', [], ['f2.java', 'f3.java']),
             ('a/b/d', [], ['f4.java'])])

        expected_tree = FileTreeNode('a', [],
                                     [FileTreeNode('b', [SourceFile('a/b/f1.java')],
                                                   [FileTreeNode('c', [SourceFile('a/b/c/f2.java'),
                                                                       SourceFile('a/b/c/f3.java')], []),
                                                    FileTreeNode('d', [SourceFile('a/b/d/f4.java')], [])])])

        self.assertEqual(tree, expected_tree)

    def test_parse_docs(self):
        test_string = '''/**
 * The result of applying a {@link Filter}.
 *
 * @since 1.0
 */
@Component
@LMAO
@API(status = STABLE, since = "1.0")
public class FilterResult {

    /**
     * Factory for creating <em>included</em> results.
     *
     * @param reason the reason why the filtered object was included
     * @return an included {@code FilterResult} with the given reason
     */
    public static FilterResult included(String reason) {
        return new FilterResult(true, reason);
    }
}'''
        Parser.parse_docs(test_string)
