from unittest import TestCase

from fmt.fmt import FiniteStateMachine
from fmt.states import CharacterEvent, MultilineCommentState, InitialState, JavadocState, SkipState, \
    AccessModifierState


class TestStates(TestCase):

    def setUp(self):
        self.fmt = FiniteStateMachine(InitialState())

    def test_InitialState(self):
        self.fmt.state = InitialState()
        test_string = 'abc'

        for index, char in enumerate(test_string):
            event = CharacterEvent(index, test_string)
            self.fmt.step(event)
            self.assertTrue(isinstance(self.fmt.state, InitialState))

    def test_MultilineCommentState(self):
        self.fmt.state = InitialState()
        test_string = '''/*xxx*/\n///*yyy*/'''

        for index, char in enumerate(test_string):
            print('from ', self.fmt.state)
            event = CharacterEvent(index, test_string)
            print('by', event)
            previous_state = self.fmt.state
            self.fmt.step(event)
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
        yyyyy*//*xx*/
        ///**/
        // /**qwerty*/'''

        for index, char in enumerate(test_string):
            print('from ', self.fmt.state)
            event = CharacterEvent(index, test_string)
            print('by', event)
            previous_state = self.fmt.state
            self.fmt.step(event)
            print('to ', self.fmt.state, '\n')

            if isinstance(self.fmt.state, MultilineCommentState) and isinstance(previous_state, MultilineCommentState):
                self.assertIn(char, 'x\n ')
            elif isinstance(self.fmt.state, JavadocState) and isinstance(previous_state, JavadocState):
                self.assertIn(char, 'y\n ')

    def test_AccessModifierState(self):
        self.fmt.state = InitialState()
        test_string = 'private\n class protected \nunprotected  void public int'

        modifiers = ''
        for index, char in enumerate(test_string):
            event = CharacterEvent(index, test_string)
            self.fmt.step(event)

            if isinstance(self.fmt.state, AccessModifierState):
                modifiers += char

        self.assertEqual(modifiers, 'privateprotectedpublic')

    def test_SkipState(self):
        event = CharacterEvent(0, ' ')
        self.fmt.state = SkipState(InitialState())

        self.assertTrue(isinstance(self.fmt.state, SkipState))
        self.fmt.step(event)
        self.assertTrue(isinstance(self.fmt.state, InitialState))

    def test_SkipState_skip_count(self):
        event = CharacterEvent(0, ' ')
        n = 5
        self.fmt.state = SkipState(InitialState(), skip_count=n)

        for i in range(n):
            self.assertTrue(isinstance(self.fmt.state, SkipState))
            self.fmt.step(event)
        self.assertTrue(isinstance(self.fmt.state, InitialState))


class TestFiniteStateMachine(TestCase):

    def setUp(self):
        self.fmt = FiniteStateMachine(InitialState())

    def test_on_event(self):
        pass
