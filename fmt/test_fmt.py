from pprint import pprint
from unittest import TestCase

from fmt.fmt import FiniteStateMachine
from fmt.states import CharacterEvent, MultilineCommentState, InitialState, JavadocState, SkipState, \
    AccessModifierState, CommentState


class TestStates(TestCase):

    def test_InitialState(self):
        self.fmt = FiniteStateMachine(InitialState())
        test_string = '  \n \t'

        for index, char in enumerate(test_string):
            event = CharacterEvent(index, test_string)
            self.fmt.step(event)
            self.assertEqual(self.fmt.state.type, 'InitialState')

    def test_MultilineCommentState(self):
        self.fmt = FiniteStateMachine(InitialState())
        test_string = '''/*xxx*/\n///*yyy*/'''

        self.fmt.process_string(test_string)

        self.assert_contains_state('MultilineCommentState', '''/*xxx*/''', self.fmt.partition)
        self.assert_contains_state('CommentState', '''///*yyy*/''', self.fmt.partition)

    def test_JavadocState(self):
        self.fmt = FiniteStateMachine(InitialState())
        test_string = '''/*xxx
        xxx
        */ /**yyyyy
        yyyyy*//*xx*/
        ///**/
        // /**qwerty*/'''

        self.fmt.process_string(test_string)

        self.assert_contains_state('MultilineCommentState', '''/*xxx
        xxx
        */''', self.fmt.partition)
        self.assert_contains_state('JavadocState', '''/**yyyyy
        yyyyy*/''', self.fmt.partition)
        self.assert_contains_state('MultilineCommentState', '''/*xx*/''', self.fmt.partition)
        self.assert_contains_state('CommentState', '''///**/''', self.fmt.partition)
        self.assert_contains_state('CommentState', '''// /**qwerty*/''', self.fmt.partition)

    def test_AccessModifierState(self):
        self.fmt = FiniteStateMachine(InitialState())
        test_string = 'private\n class protected \nunprotected  void public int'

        self.fmt.process_string(test_string)

        self.assert_contains_state('AccessModifierState', 'private', self.fmt.partition)
        self.assert_contains_state('AccessModifierState', 'protected', self.fmt.partition)
        self.assert_contains_state('NameState', 'unprotected', self.fmt.partition)
        self.assert_contains_state('AccessModifierState', 'public', self.fmt.partition)

    def test_SkipState(self):
        self.fmt = FiniteStateMachine(SkipState(InitialState()))
        event = CharacterEvent(0, ' ')

        self.assertTrue(isinstance(self.fmt.state, SkipState))
        self.assertEqual(self.fmt.state.type, 'InitialState')
        self.fmt.step(event)
        self.assertTrue(isinstance(self.fmt.state, InitialState))
        self.assertEqual(self.fmt.state.type, 'InitialState')

    def test_SkipState_skip_count(self):
        n = 5
        self.fmt = FiniteStateMachine(SkipState(InitialState(), skip_count=n, pretend='CommentState'))
        event = CharacterEvent(0, ' ')

        for i in range(n):
            self.assertTrue(isinstance(self.fmt.state, SkipState))
            self.assertEqual(self.fmt.state.type, 'CommentState')
            self.fmt.step(event)

        self.assertTrue(isinstance(self.fmt.state, InitialState))
        self.assertEqual(self.fmt.state.type, 'InitialState')

    def test_SkipState_activate(self):
        self.fmt = FiniteStateMachine(SkipState(InitialState(), skip_count=2, activate=True))
        test_string = ' //abc'

        self.assertTrue(isinstance(self.fmt.state, SkipState))
        self.assertEqual(self.fmt.state.type, 'InitialState')

        self.fmt.step(event=CharacterEvent(0, test_string))  # skipped
        self.fmt.step(event=CharacterEvent(1, test_string))
        self.assertEqual(self.fmt.state.type, 'CommentState')

    def assert_contains_state(self, state_type, string_value, container):
        self.assertIn((state_type, list(string_value)), container)


class TestFiniteStateMachine(TestCase):

    def setUp(self):
        self.fmt = FiniteStateMachine(InitialState())

    def test_on_event(self):
        pass
