from abc import ABC, abstractmethod

from lexer.util import CharacterEvent


# todo metaclass singleton
class State(ABC):
    separated = False

    @abstractmethod
    def on_event(self, event) -> 'State':
        pass

    @property
    def type(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return self.__class__.__name__


class WhitespaceState(State):

    def on_event(self, event: CharacterEvent) -> State:
        if event.character_met.isspace():
            return self

        return InitialState().on_event(event)


class InitialState(State):

    def on_event(self, event: CharacterEvent) -> State:
        if event.character_met == '/':
            lookahead = event.lookahead(2)

            if lookahead[0] == '*':
                if lookahead[1] == '*':
                    return SkipState(JavadocState(), skip_count=2)
                else:
                    return SkipState(MultilineCommentState())
            elif lookahead[0] == '/':
                return SkipState(CommentState())

        elif event.character_met == '.':
            return SkipState(InitialState(), activate=True, as_state='DelimiterState')
        elif event.character_met == ',':
            return SkipState(InitialState(), activate=True, as_state='DelimiterState')
        elif event.character_met == ';':
            return SkipState(InitialState(), activate=True, as_state='DelimiterState')

        elif event.character_met == '{':
            return SkipState(InitialState(), activate=True, as_state='OpenBracketState', separated=True)
        elif event.character_met == '}':
            return SkipState(InitialState(), activate=True, as_state='ClosedBracketState', separated=True)

        elif event.character_met == '(':
            return SkipState(InitialState(), activate=True, as_state='OpenParenthesisState')
        elif event.character_met == ')':
            return SkipState(InitialState(), activate=True, as_state='ClosedParenthesisState')
        elif event.character_met == '@':
            return AnnotationState()

        elif event.is_start_of('class'):
            return SkipState(InitialState(), activate=True, skip_count=5, as_state='IdentifierState')
        elif event.is_start_of('interface'):
            return SkipState(InitialState(), activate=True, skip_count=9, as_state='IdentifierState')
        elif event.is_start_of('enum'):
            return SkipState(InitialState(), activate=True, skip_count=4, as_state='IdentifierState')

        elif event.is_start_of('static'):
            return SkipState(InitialState(), activate=True, skip_count=6, as_state='ModifierState')
        elif event.is_start_of('abstract'):
            return SkipState(InitialState(), activate=True, skip_count=8, as_state='ModifierState')
        elif event.is_start_of('default'):
            return SkipState(InitialState(), activate=True, skip_count=7, as_state='ModifierState')
        elif event.is_start_of('final'):
            return SkipState(InitialState(), activate=True, skip_count=5, as_state='ModifierState')
        elif event.character_met == '<':
            return MethodGenericState()

        elif event.is_start_of('extends'):
            return SkipState(InitialState(), activate=True, skip_count=7, as_state='IdentifierState')
        elif event.is_start_of('implements'):
            return SkipState(InitialState(), activate=True, skip_count=10, as_state='IdentifierState')
        elif event.is_start_of('import'):
            return SkipState(InitialState(), activate=True, skip_count=6, as_state='IdentifierState')
        elif event.is_start_of('package'):
            return SkipState(InitialState(), activate=True, skip_count=7, as_state='IdentifierState')

        elif event.is_start_of('protected'):
            return SkipState(InitialState(), activate=True, skip_count=9, as_state='AccessModifierState')
        elif event.is_start_of('private'):
            return SkipState(InitialState(), activate=True, skip_count=7, as_state='AccessModifierState')
        elif event.is_start_of('public'):
            return SkipState(InitialState(), activate=True, skip_count=6, as_state='AccessModifierState')

        elif event.character_met.isidentifier():
            return NameState()
        elif event.character_met.isspace():
            return WhitespaceState()

        return self


class CommentState(State):

    def on_event(self, event: CharacterEvent) -> State:
        if event.character_met == '\n':
            return InitialState()

        return self


class MultilineCommentState(State):

    def on_event(self, event: CharacterEvent) -> State:
        if event.character_met == '*' and event.lookahead(1) == '/':
            return SkipState(InitialState(), activate=True, skip_count=2, as_state=self.type)

        return self


class JavadocState(State):

    def on_event(self, event: CharacterEvent) -> State:
        if event.character_met == '*' and event.lookahead(1) == '/':
            return SkipState(InitialState(), activate=True, skip_count=2, as_state=self.type)

        return self


class NameState(State):

    def on_event(self, event: CharacterEvent) -> State:
        if event.character_met.isidentifier() or event.character_met.isnumeric() \
                or event.character_met in ['<', '>']:
            return self

        if event.character_met == '.':
            return SkipState(InitialState(), activate=True, as_state='DelimiterState')

        if event.character_met == '(':  # todo can be space before parenthesis
            return ArgumentsParenthesisState()

        return InitialState().on_event(event)


class MethodGenericState(State):

    def on_event(self, event: CharacterEvent) -> State:
        if event.character_met == '>':
            return SkipState(InitialState(), activate=True, as_state=self.type)

        if event.character_met.isspace() or event.character_met.isidentifier() or event.character_met.isnumeric() \
                or event.character_met in ['?']:
            return self

        return InitialState().on_event(event)

    @property
    def type(self) -> str:
        return 'ModifierState'


class ArgumentsParenthesisState(State):

    def on_event(self, event: CharacterEvent) -> State:
        if event.character_met == ')':
            return SkipState(InitialState(), activate=True, as_state=self.type)
        elif event.character_met.isidentifier() or event.character_met.isnumeric() \
                or event.character_met in ['<', '>', ',', '[', ']', '?', '.'] or event.character_met.isspace():
            return self

        return InitialState().on_event(event)


class AnnotationState(State):

    def on_event(self, event: CharacterEvent) -> State:
        if event.character_met.isalpha():
            return self

        if event.character_met == '(':
            return AnnotationBracketsState()

        return InitialState()


class AnnotationBracketsState(State):

    def on_event(self, event: CharacterEvent) -> State:
        if event.character_met == ')':
            return SkipState(InitialState(), activate=True, as_state=self.type)

        return self

    @property
    def type(self) -> str:
        return AnnotationState.__name__


class SkipState(State):

    def __init__(self, next_state: State, activate=False, skip_count=1, as_state=None, separated=False):
        self.count = skip_count
        self.next_state = next_state
        self._activate_next_state = activate
        self._type = next_state.type if not as_state else as_state
        self.separated = separated

    def on_event(self, event) -> State:
        if self.count > 1:
            self.count -= 1
            return self

        if self._activate_next_state:
            return self.next_state.on_event(event)

        return self.next_state

    @property
    def type(self) -> str:
        return self._type
