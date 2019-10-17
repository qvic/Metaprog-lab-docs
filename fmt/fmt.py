from fmt.states import InitialState, State


class FiniteStateMachine:

    def __init__(self, initial_state: State):
        self.state = initial_state

    def on_event(self, event):
        self.state = self.state.on_event(event)
