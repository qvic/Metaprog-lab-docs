from abc import ABC, abstractmethod


class Event:

    def __init__(self, character_met, lookahead):
        self.character_met = character_met
        self.lookahead = lookahead

    def __repr__(self) -> str:
        return 'Event[{0}:{1}]'.format(repr(self.character_met), repr(self.lookahead))


# todo metaclass singleton
class State(ABC):

    @abstractmethod
    def on_event(self, event: Event):
        pass

    def __repr__(self) -> str:
        return self.__class__.__name__


class InitialState(State):

    def on_event(self, event: Event) -> State:
        if event.character_met == '/':
            if event.lookahead == '*':
                return SkipState(MultilineCommentState())
            elif event.lookahead == '/':
                return SkipState(CommentState())

        return self


class CommentState(State):

    def on_event(self, event: Event) -> State:
        if event.character_met == '\n':
            return InitialState()

        return self


class MultilineCommentState(State):

    def on_event(self, event: Event) -> State:
        if event.character_met == '*':
            if event.lookahead == '/':
                return SkipState(InitialState())
            else:
                return JavadocState()

        return self


class JavadocState(State):

    def on_event(self, event: Event) -> State:
        if event.character_met == '*' and event.lookahead == '/':
            return SkipState(InitialState())

        return self


class SkipState(State):

    def __init__(self, next_state: State, skip_count=1):
        self.count = skip_count
        self.next_state = next_state

    def on_event(self, event: Event) -> State:
        if self.count > 1:
            self.count -= 1
            return self

        return self.next_state
