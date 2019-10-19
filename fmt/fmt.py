from fmt.states import InitialState, State, CharacterEvent


class FiniteStateMachine:

    def __init__(self, initial_state: State):
        self.state = initial_state
        self.partition = []
        self._current_series = []

    def process_string(self, string: str):
        for index, char in enumerate(string):
            self.step(CharacterEvent(index, string))
        self.step(CharacterEvent(len(string), string))
        return self.partition

    def step(self, event: CharacterEvent):
        _previous_state = self.state
        self.state = self.state.on_event(event)

        if event.eof or _previous_state.type != self.state.type:
            self.partition.append((_previous_state.type, self._current_series))
            self._current_series = []

        self._current_series.append(event.character_met)
