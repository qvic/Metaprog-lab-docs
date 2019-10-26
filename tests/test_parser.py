from pprint import pprint
from unittest import TestCase

from lexer.util import Token, LexerPartition
from parser.fmt import FiniteStateMachine
from parser.parser import Parser
from parser.states import InitialState
from util.util import FileTreeNode, SourceFile, DocumentedClass, DocumentedMethod



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

    def test_parse_docs_for_class_with_all_elements(self):
        test_string = '''/**
 * The result of applying a {@link Filter}.
 *
 * @since 1.0
 */
@Component
@API(status = STABLE, since = "1.0")
public class FilterResult extends AbstractFilterResult implements Result, Serializable {}'''

        classes = Parser.parse_docs(test_string)

        self.assertEqual(
            DocumentedClass.create('''/**
 * The result of applying a {@link Filter}.
 *
 * @since 1.0
 */''', ['@Component', '@API(status = STABLE, since = "1.0")'], 'public', [], 'FilterResult',
                                   'AbstractFilterResult', ['Result', 'Serializable'],
                                   [], []),
            classes[0])

    def test_parse_docs_for_class_without_extends(self):
        test_string = '''/**
 * The result of applying a {@link Filter}.
 *
 * @since 1.0
 */
@Component
@API(status = STABLE, since = "1.0")
public class FilterResult implements Result, Serializable {}'''

        classes = Parser.parse_docs(test_string)

        self.assertEqual(
            DocumentedClass.create('''/**
 * The result of applying a {@link Filter}.
 *
 * @since 1.0
 */''', ['@Component', '@API(status = STABLE, since = "1.0")'], 'public', [], 'FilterResult',
                                   None, ['Result', 'Serializable'],
                                   [], []),
            classes[0])

    def test_parse_docs_for_class_without_implements(self):
        test_string = '''/**
 * The result of applying a {@link Filter}.
 *
 * @since 1.0
 */
@Component
@API(status = STABLE, since = "1.0")
public class FilterResult extends AbstractFilterResult {}'''

        classes = Parser.parse_docs(test_string)

        self.assertEqual(
            DocumentedClass.create('''/**
 * The result of applying a {@link Filter}.
 *
 * @since 1.0
 */''', ['@Component', '@API(status = STABLE, since = "1.0")'], 'public', [], 'FilterResult',
                                   'AbstractFilterResult', [],
                                   [], []),
            classes[0])

    def test_parse_docs_for_class_without_annotations(self):
        test_string = '''/**
 * The result of applying a {@link Filter}.
 *
 * @since 1.0
 */
public class FilterResult extends AbstractFilterResult implements Result, Serializable {}'''

        classes = Parser.parse_docs(test_string)

        self.assertEqual(
            DocumentedClass.create('''/**
 * The result of applying a {@link Filter}.
 *
 * @since 1.0
 */''', [], 'public', [], 'FilterResult', 'AbstractFilterResult', ['Result', 'Serializable'], [], []),
            classes[0])

    def test_parse_docs_for_class_without_javadoc(self):
        test_string = '''@Component public class FilterResult extends AbstractFilterResult implements Result, Serializable {}'''

        classes = Parser.parse_docs(test_string)

        self.assertEqual(
            DocumentedClass.create(None, ['@Component'], 'public', [], 'FilterResult', 'AbstractFilterResult',
                                   ['Result', 'Serializable'], [], []),
            classes[0])

        def test_parse_docs_for_class_with_all_elements(self):
            test_string = '''/**
     * The result of applying a {@link Filter}.
     *
     * @since 1.0
     */
    @Component
    @API(status = STABLE, since = "1.0")
    public class FilterResult extends AbstractFilterResult implements Result, Serializable {}'''

            classes = Parser.parse_docs(test_string)

            self.assertEqual(
                DocumentedClass.create('''/**
     * The result of applying a {@link Filter}.
     *
     * @since 1.0
     */''', ['@Component', '@API(status = STABLE, since = "1.0")'], 'public', [], 'FilterResult',
                                       'AbstractFilterResult', ['Result', 'Serializable'],
                                       [], []),
                classes[0])

    def test_parse_docs_for_class_with_static_and_final(self):
        test_string = '''/**
 * The result of applying a {@link Filter}.
 *
 * @since 1.0
 */
@Component
@API(status = STABLE, since = "1.0")
public static final class FilterResult extends AbstractFilterResult implements Result, Serializable {}'''

        classes = Parser.parse_docs(test_string)

        self.assertEqual(
            DocumentedClass.create('''/**
 * The result of applying a {@link Filter}.
 *
 * @since 1.0
 */''', ['@Component', '@API(status = STABLE, since = "1.0")'], 'public', ['static', 'final'], 'FilterResult',
                                   'AbstractFilterResult', ['Result', 'Serializable'],
                                   [], []),
            classes[0])

    def test_parse_docs_for_methods(self):
        test_string = '''
public final class A {

    /**
     * Docs for included
     */
    public FilterResult included(String reason) {
        return new FilterResult(true, reason);
    }

    static class InnerClass {
        /**
         * Docs for innerClassMethod
         */
        public void innerClassMethod() {}
    }
    
    /**
     * Docs for get
     */
    @Bean
    protected static final Type get(Type arg) {}

    static final boolean getValue() {}
    /**
     * Docs for main
     */
    public static void main(String[] args) {}

    @Bean
    @Override
    public String toString() {
        return this.name;
    }
}'''
        classes = Parser.parse_docs(test_string)

        self.assertEqual(
            DocumentedClass.create(None, [], 'public', ['final'],
                                   'A',
                                   None, [],
                                   [DocumentedMethod.create('''/**
     * Docs for included
     */''', [], 'public', [], 'FilterResult', 'included', [['String', 'reason']]),
                                    DocumentedMethod.create('''/**
     * Docs for get
     */''', ['@Bean'], 'protected', ['static', 'final'], 'Type', 'get', [['Type', 'arg']]),
                                    DocumentedMethod.create(None, [], 'package-private', ['static', 'final'], 'boolean',
                                                            'getValue', []),
                                    DocumentedMethod.create('''/**
     * Docs for main
     */''', [], 'public', ['static'], 'void', 'main', [['String[]', 'args']]),
                                    DocumentedMethod.create(None, ['@Bean', '@Override'], 'public', [], 'String',
                                                            'toString',
                                                            [])],
                                   [DocumentedClass.create(None, [], 'package-private', ['static'], 'InnerClass', None,
                                                           [], [
                                                               DocumentedMethod.create('''/**
         * Docs for innerClassMethod
         */''', [], 'public', [], 'void',
                                                                                       'innerClassMethod', [])],
                                                           [])]),
            classes[0])

    def test_parse_docs(self):
        test_string = '''/**
 * The result of applying a {@link Filter}.
 *
 * @since 1.0
 */
@Component
@API(status = STABLE, since = "1.0")
public class FilterResult extends AbstractFilterResult implements Result, Serializable {

    /**
     * Factory for creating <em>included</em> results.
     *
     * @param reason the reason why the filtered object was included
     * @return an included {@code FilterResult} with the given reason
     */
    public FilterResult included(String reason) {
        return new FilterResult(true, reason);
    }
    
    static class InnerClass {
        
        public void innerClassMethod() {}
    }
    
    /**
     * Overriding toString
     */
    @Override
    public String toString() {
        return this.name;
    }
}'''
        classes = Parser.parse_docs(test_string)

        self.assertEqual(
            DocumentedClass.create('''/**
 * The result of applying a {@link Filter}.
 *
 * @since 1.0
 */''', ['@Component', '@API(status = STABLE, since = "1.0")'], 'public', [], 'FilterResult',
                                   'AbstractFilterResult', ['Result', 'Serializable'],
                                   [DocumentedMethod.create('''/**
     * Factory for creating <em>included</em> results.
     *
     * @param reason the reason why the filtered object was included
     * @return an included {@code FilterResult} with the given reason
     */''', [], 'public', [], 'FilterResult', 'included', [['String', 'reason']]),
                                    DocumentedMethod.create('''/**
     * Overriding toString
     */''', ['@Override'], 'public', [], 'String', 'toString', [])],
                                   [DocumentedClass.create(None, [], 'package-private', ['static'], 'InnerClass', None,
                                                           [], [
                                                               DocumentedMethod.create(None, [], 'public', [], 'void',
                                                                                       'innerClassMethod', [])],
                                                           [])]),
            classes[0])
