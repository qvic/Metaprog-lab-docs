import itertools
from abc import ABC, abstractmethod


class CharacterEvent:

    def __init__(self, character_index: int, file_contents: str):
        self.eof = character_index >= len(file_contents)
        self.character_met = '' if self.eof else file_contents[character_index]
        self._lookahead = itertools.islice(file_contents, character_index + 1, len(file_contents))

    def __repr__(self) -> str:
        return 'CharacterEvent[{0}]'.format(repr(self.character_met))

    def lookahead(self, n):
        return ''.join(itertools.islice(self._lookahead, n))


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
        elif event.character_met == 'p':
            lookahead = event.lookahead(8)

            if lookahead == 'rotected' or \
                    lookahead[:6] == 'rivate' or \
                    lookahead[:5] == 'ublic':
                return AccessModifierState()
        elif event.character_met.isalpha():
            return NameState()
        return self


class CommentState(State):

    def on_event(self, event: CharacterEvent) -> State:
        if event.character_met == '\n':
            return InitialState()

        return self


class MultilineCommentState(State):

    def on_event(self, event: CharacterEvent) -> State:
        if event.character_met == '*':
            if event.lookahead(1) == '/':
                return SkipState(InitialState(), skip_count=2, pretend=self.type)
            else:
                return JavadocState()

        return self


class JavadocState(State):

    def on_event(self, event: CharacterEvent) -> State:
        if event.character_met == '*' and event.lookahead(1) == '/':
            return SkipState(InitialState(), activate=True, skip_count=2, pretend=self.type)

        return self


class AccessModifierState(State):

    def on_event(self, event: CharacterEvent) -> State:
        if event.character_met.isspace():
            return InitialState()

        return self


class NameState(State):

    def on_event(self, event: CharacterEvent) -> State:
        if event.character_met.isspace():
            return InitialState()

        return self


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
