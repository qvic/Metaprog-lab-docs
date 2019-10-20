from fmt.states import InitialState, State, CharacterEvent


class FiniteStateMachine:

    def __init__(self, initial_state: State):
        self.state = initial_state
        self.partition = []
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
            self.partition.append((_previous_state.type, self._current_series))
            self._current_series = []

        self._current_series.append(event.character_met)

    @property
    def string_partition(self):
        return [(state_type, ''.join(string_value)) for state_type, string_value in self.partition]
