import itertools


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
