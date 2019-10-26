from pprint import pprint
from unittest import TestCase

from lexer.util import Token, LexerPartition
from parser.fmt import FiniteStateMachine
from parser.states import InitialState
from util.util import DocumentedClass, DocumentedInterface, DocumentedMethod


class TestFMT(TestCase):

    def test_partition_for_class_1(self):
        test_list = [Token('IdentifierState', 'class'), Token('NameState', 'X<T>'), Token('IdentifierState', 'extends'),
                     Token('NameState', 'E'),
                     Token('OpenBracketState', '{')]

        partition = LexerPartition()
        partition.sequence = test_list

        fmt = FiniteStateMachine(InitialState())
        fmt.process_tokens(partition)

        obj = DocumentedClass.from_partition(fmt._partition)
        self.assertEqual(obj, DocumentedClass.create(None, [], None, [], 'X<T>', 'E', [], [], []))

    def test_partition_for_class_2(self):
        test_list = [Token('JavadocState', 'doc2'), Token('AnnotationState', '@a'),
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

        obj = DocumentedClass.from_partition(fmt._partition)
        self.assertEqual(obj,
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

        obj = DocumentedClass.from_partition(fmt._partition)
        self.assertEqual(obj, DocumentedInterface.create(None, [], None, [], 'X<T>', ['E', 'Y'], [], []))

    def test_partition_for_method(self):
        test_list = [Token('NameState', 'void'), Token('NameState', 'method'),
                     Token('ArgumentsParenthesisState', '(String arg, int arg)'),
                     Token('OpenBracketState', '{')]

        partition = LexerPartition()
        partition.sequence = test_list

        fmt = FiniteStateMachine(InitialState())
        fmt.process_tokens(partition)

        obj = DocumentedClass.from_partition(fmt._partition)
        self.assertEqual(obj, DocumentedMethod.create(None, [], None, [], 'void', 'method',
                                                      [['String', 'arg'], ['int', 'arg']]))