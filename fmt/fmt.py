from fmt.states import InitialState, State


class FiniteStateMachine:

    def __init__(self, initial_state: State):
        self.state = initial_state

    def step(self, event):
        self.state = self.state.on_event(event)
        # todo parsed array - string with marked segments by states
