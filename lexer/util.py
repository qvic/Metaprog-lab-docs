import itertools

from util.util import Representable


class CharacterEvent:

    def __init__(self, character_index: int, file_contents: str):
        self.eof = character_index >= len(file_contents)
        self.character_met = '' if self.eof else file_contents[character_index]
        self._lookahead = file_contents[character_index + 1:]

    def __repr__(self) -> str:
        return 'CharacterEvent[{0}]'.format(repr(self.character_met))

    def lookahead(self, n) -> str:
        n_lookahead = list(itertools.islice(self._lookahead, n))
        n_lookahead.extend([' '] * (n - len(n_lookahead)))
        return ''.join(n_lookahead)

    def is_start_of(self, string: str) -> bool:
        return string == self.character_met + self._lookahead[:len(string) - 1]


class Token(Representable):

    def __init__(self, state, value):
        self.value = value
        self.state = state

    def __eq__(self, other: object) -> bool:
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False


class LexerPartition(Representable):

    def __init__(self, partition_list=None):
        if partition_list is None:
            partition_list = []

        self.sequence = self._generate_string_partition(partition_list)

    @staticmethod
    def _generate_string_partition(partition_list):
        return tuple(Token(state_type, ''.join(string_value)) for state_type, string_value in partition_list)

    def exclude(self, *args) -> 'LexerPartition':
        partition = LexerPartition()
        partition.sequence = tuple(item for item in self.sequence if all(arg != item.state for arg in args))
        return partition

    def state_at(self, index):
        try:
            return self.sequence[index].state
        except IndexError:
            return None

    def value_at(self, index):
        try:
            return self.sequence[index].value
        except IndexError:
            return None

    def token_at(self, index):
        try:
            return self.sequence[index]
        except IndexError:
            return None

