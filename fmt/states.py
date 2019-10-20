from abc import ABC, abstractmethod

from fmt.util import CharacterEvent


# todo metaclass singleton
class State(ABC):

    @abstractmethod
    def on_event(self, event: CharacterEvent) -> 'State':
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
        elif event.character_met == '{':
            return SkipState(InitialState(), activate=True, pretend='OpenBracketState')
        elif event.character_met == '}':
            return SkipState(InitialState(), activate=True, pretend='ClosedBracketState')
        elif event.character_met == '@':
            return AnnotationState()
        elif event.is_start_of('class'):
            return SkipState(InitialState(), activate=True, skip_count=5, pretend='IdentifierState')
        elif event.is_start_of('protected'):
            return SkipState(InitialState(), activate=True, skip_count=9, pretend='AccessModifierState')
        elif event.is_start_of('private'):
            return SkipState(InitialState(), activate=True, skip_count=7, pretend='AccessModifierState')
        elif event.is_start_of('public'):
            return SkipState(InitialState(), activate=True, skip_count=6, pretend='AccessModifierState')
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
            return SkipState(InitialState(), activate=True, skip_count=2, pretend=self.type)

        return self


class JavadocState(State):

    def on_event(self, event: CharacterEvent) -> State:
        if event.character_met == '*' and event.lookahead(1) == '/':
            return SkipState(InitialState(), activate=True, skip_count=2, pretend=self.type)

        return self


class NameState(State):

    def on_event(self, event: CharacterEvent) -> State:
        if event.character_met.isidentifier():
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
            return SkipState(InitialState(), activate=True, pretend=self.type)

        return self

    @property
    def type(self) -> str:
        return AnnotationState.__name__


class SkipState(State):

    def __init__(self, next_state: State, activate=False, skip_count=1, pretend=None):
        self.count = skip_count
        self.next_state = next_state
        self._activate_next_state = activate
        self._type = next_state.type if not pretend else pretend

    def on_event(self, event: CharacterEvent) -> State:
        if self.count > 1:
            self.count -= 1
            return self

        if self._activate_next_state:
            return self.next_state.on_event(event)

        return self.next_state

    @property
    def type(self) -> str:
        return self._type
