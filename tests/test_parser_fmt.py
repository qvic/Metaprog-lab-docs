from pprint import pprint
from unittest import TestCase

from lexer.util import Token, LexerPartition
from parser.fmt import FiniteStateMachine
from parser.parser import Parser
from parser.states import InitialState
from util.util import DocumentedClass, DocumentedInterface, DocumentedMethod


class TestFMT(TestCase):

    def test_partition_for_class_1(self):
        test_list = [Token('IdentifierState', 'class'), Token('IdentifierState', 'extends'),
                     Token('IdentifierState', 'class'),
                     Token('NameState', 'E'),
                     Token('OpenBracketState', '{')]

        partition = LexerPartition()
        partition.sequence = test_list

        fmt = FiniteStateMachine(InitialState())
        fmt.process_tokens(partition)

        iterator = Parser.from_partition(fmt._partition)
        self.assertEqual(next(iterator), DocumentedClass.create(None, [], None, [], 'E', None, [], [], []))

    def test_partition_for_class_2(self):
        test_list = [Token('JavadocState', 'doc1'), Token('JavadocState', 'doc2'), Token('AnnotationState', '@a'),
                     Token('AnnotationState', '@b'),
                     Token('AccessModifierState', 'public'), Token('ModifierState', 'static'),
                     Token('IdentifierState', 'class'), Token('NameState', 'A'),
                     Token('IdentifierState', 'extends'), Token('NameState', 'B'),
                     Token('IdentifierState', 'implements'), Token('NameState', 'C'), Token('DelimiterState', ','),
                     Token('NameState', 'D'), Token('OpenBracketState', '{')]

        partition = LexerPartition()
        partition.sequence = test_list

        fmt = FiniteStateMachine(InitialState())
        fmt.process_tokens(partition)

        iterator = Parser.from_partition(fmt._partition)
        self.assertEqual(next(iterator),
                         DocumentedClass.create('doc2', ['@a', '@b'], 'public', ['static'], 'A', 'B', ['C', 'D'], [],
                                                []))

    def test_partition_for_interface(self):
        test_list = [Token('IdentifierState', 'interface'), Token('NameState', 'X<T>'),
                     Token('IdentifierState', 'extends'),
                     Token('NameState', 'E'), Token('DelimiterState', ','), Token('NameState', 'Y'),
                     Token('OpenBracketState', '{')]

        partition = LexerPartition()
        partition.sequence = test_list

        fmt = FiniteStateMachine(InitialState())
        fmt.process_tokens(partition)

        iterator = Parser.from_partition(fmt._partition)
        self.assertEqual(next(iterator), DocumentedInterface.create(None, [], None, [], 'X<T>', ['E', 'Y'], [], []))

    def test_partition_for_method(self):
        test_list = [Token('NameState', 'void'), Token('NameState', 'method'),
                     Token('ArgumentsParenthesisState', '(String arg, int arg)'),
                     Token('OpenBracketState', '{')]

        partition = LexerPartition()
        partition.sequence = test_list

        fmt = FiniteStateMachine(InitialState())
        fmt.process_tokens(partition)

        iterator = Parser.from_partition(fmt._partition)
        self.assertEqual(next(iterator), DocumentedMethod.create(None, [], None, [], 'void', 'method',
                                                                 [['String', 'arg'], ['int', 'arg']]))

    def test_parser(self):
        test_list = [Token('IdentifierState', 'class'), Token('NameState', 'X<T>'), Token('IdentifierState', 'extends'),
                     Token('NameState', 'E'), Token('OpenBracketState', '{'), Token('NameState', 'void'),
                     Token('NameState', 'method'),
                     Token('ArgumentsParenthesisState', '(String arg, int arg)'),
                     Token('OpenBracketState', '{')]

        partition = LexerPartition()
        partition.sequence = test_list

        fmt = FiniteStateMachine(InitialState())
        fmt.process_tokens(partition)

        iterator = Parser.from_partition(fmt._partition)

        self.assertEqual(next(iterator), DocumentedClass.create(None, [], None, [], 'X<T>', 'E', [], [], []))
        self.assertEqual(next(iterator), '{')
        self.assertEqual(next(iterator), DocumentedMethod.create(None, [], None, [], 'void', 'method',
                                                                 [['String', 'arg'], ['int', 'arg']]))
        self.assertEqual(next(iterator), '{')
