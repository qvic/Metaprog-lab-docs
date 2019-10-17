from unittest import TestCase
from itertools import zip_longest

from fmt.fmt import FiniteStateMachine
from fmt.states import Event, MultilineCommentState, InitialState, CommentState, JavadocState, SkipState


class TestStates(TestCase):

    def setUp(self):
        self.fmt = FiniteStateMachine(InitialState())

    def test_InitialState(self):
        self.fmt.state = InitialState()
        test_string = 'abc'

        for char, lookahead in zip_longest(test_string, test_string[1:]):
            event = Event(char, lookahead)
            self.fmt.on_event(event)
            self.assertTrue(isinstance(self.fmt.state, InitialState))

    def test_MultilineCommentState(self):
        self.fmt.state = InitialState()
        test_string = '''/*xxx*/\n///*yyy*/'''

        for char, lookahead in zip_longest(test_string, test_string[1:]):
            print('from ', self.fmt.state)

            event = Event(char, lookahead)
            print('by', event)
            previous_state = self.fmt.state
            self.fmt.on_event(event)
            print('to ', self.fmt.state, '\n')

            if isinstance(self.fmt.state, MultilineCommentState) and isinstance(previous_state, MultilineCommentState):
                self.assertEqual(char, 'x')

            if char == 'x':
                self.assertTrue(isinstance(self.fmt.state, MultilineCommentState))

    def test_JavadocState(self):
        self.fmt.state = InitialState()
        test_string = '''/*xxx
        xxx
        */ /**yyyyy
        yyyyy*/
        ///**/
        // /**qwerty*/'''

        for char, lookahead in zip_longest(test_string, test_string[1:]):
            print('from ', self.fmt.state)

            event = Event(char, lookahead)
            print('by', event)
            previous_state = self.fmt.state
            self.fmt.on_event(event)
            print('to ', self.fmt.state, '\n')

            if isinstance(self.fmt.state, MultilineCommentState) and isinstance(previous_state, MultilineCommentState):
                self.assertIn(char, 'x\n ')
            elif isinstance(self.fmt.state, JavadocState) and isinstance(previous_state, JavadocState):
                self.assertIn(char, 'y\n ')

    def test_SkipState(self):
        event = Event(None, None)
        self.fmt.state = SkipState(InitialState())

        self.assertTrue(isinstance(self.fmt.state, SkipState))
        self.fmt.on_event(event)
        self.assertTrue(isinstance(self.fmt.state, InitialState))

    def test_SkipState_skip_count(self):
        event = Event(None, None)
        n = 5
        self.fmt.state = SkipState(InitialState(), skip_count=n)

        for i in range(n):
            self.assertTrue(isinstance(self.fmt.state, SkipState))
            self.fmt.on_event(event)
        self.assertTrue(isinstance(self.fmt.state, InitialState))


class TestFiniteStateMachine(TestCase):

    def setUp(self):
        self.fmt = FiniteStateMachine(InitialState())

    def test_on_event(self):
        pass
