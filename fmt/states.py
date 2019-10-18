import itertools
from abc import ABC, abstractmethod


class CharacterEvent:

    def __init__(self, character_index: int, file_contents: str):
        self.character_met: str = file_contents[character_index]
        self._lookahead = itertools.islice(file_contents, character_index + 1, len(file_contents))

    def __repr__(self) -> str:
        return 'CharacterEvent[{0}]'.format(repr(self.character_met))

    def lookahead(self, n):
        return ''.join(itertools.islice(self._lookahead, n))


# todo metaclass singleton
class State(ABC):

    @abstractmethod
    def on_event(self, event: CharacterEvent):
        pass

    def __repr__(self) -> str:
        return self.__class__.__name__


class InitialState(State):

    def on_event(self, event: CharacterEvent) -> State:
        if event.character_met == '/':
            lookahead = event.lookahead(1)

            if lookahead == '*':
                return SkipState(MultilineCommentState())
            elif lookahead == '/':
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
                return SkipState(InitialState())
            else:
                return JavadocState()

        return self


class JavadocState(State):

    def on_event(self, event: CharacterEvent) -> State:
        if event.character_met == '*' and event.lookahead(1) == '/':
            return SkipState(InitialState())

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

    def __init__(self, next_state: State, skip_count=1):
        self.count = skip_count
        self.next_state = next_state

    def on_event(self, event: CharacterEvent) -> State:
        if self.count > 1:
            self.count -= 1
            return self

        return self.next_state
