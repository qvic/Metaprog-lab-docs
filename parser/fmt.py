from pprint import pprint
from typing import List

from lexer.states import State
from lexer.util import LexerPartition, Token


class TokenEvent:

    def __init__(self, token: Token, lookahead: List[Token], end=False):
        self.token = token
        self.end = end
        self._lookahead = lookahead

    def __repr__(self) -> str:
        return 'TokenEvent[{0}]'.format(repr(self.token))

    def lookahead(self, n) -> List[Token]:
        return self._lookahead[:n]


class FiniteStateMachine:

    def __init__(self, initial_state: State):
        self.initial_state = initial_state
        self.state = initial_state
        self._partition = []
        self._current_series = []
        self._last_initial_index = 0

    def process_tokens(self, partition: LexerPartition):
        i = 0
        previous_state = None

        while i < len(partition.sequence):
            token = partition.sequence[i]
            event = TokenEvent(token, partition.sequence[i + 1:])

            self.step(event)  # todo generator for lookahead

            if self.state.type == 'DeadState':
                if previous_state is not None and previous_state.type == 'InitialState':
                    i += 1
                # self._append_to_partition(self.state)
                self._current_series = []
                self._partition = [] # or delete to latest delimiter
                self.state = self.initial_state
            else:
                i += 1

            previous_state = self.state

            pprint(self._partition, width=150)
            print()
            # on dead state discard tokens until initialstate
        self._partition.append((self.state.type, self._current_series))

    def step(self, event: TokenEvent):
        _previous_state = self.state
        self.state = self.state.on_event(event)

        if _previous_state.type != self.state.type:
            self._append_to_partition(_previous_state)

        self._current_series.append(event.token)

    def _append_to_partition(self, new_state):
        self._partition.append((new_state.type, self._current_series))
        self._current_series = []
