from lexer.states import InitialState, State, CharacterEvent
from lexer.util import LexerPartition, Token


class FiniteStateMachine:

    def __init__(self, initial_state: State):
        self.state = initial_state
        self._partition = []
        self._current_series = []

    def process_string(self, string: str, end=True):
        for index, char in enumerate(string):
            self.step(CharacterEvent(index, string))
        if end:
            self.step(CharacterEvent(len(string), string))

    def step(self, event: CharacterEvent):
        _previous_state = self.state
        self.state = self.state.on_event(event)

        if event.eof or _previous_state.type != self.state.type:
            self._partition.append((_previous_state.type, self._current_series))
            self._current_series = []

        self._current_series.append(event.character_met)

    @property
    def partition(self) -> LexerPartition:
        return LexerPartition(self._partition)
