from enum import Enum


def get_subsequences(seq, exclude_indices):
    """
    >>> get_subsequences('abcdef', [(1, 3), (4, 5)])
    ['a', 'd', 'f']

    >>> get_subsequences([1,2,3,4,5,6], [(1, 3), (3, 5)])
    [[1], [6]]
    """
    subsequences = []
    start = 0

    for index_pair in exclude_indices:
        end = index_pair[0]
        if start < end:
            subsequences.append(seq[start:end])
        start = index_pair[1]

    if start < len(seq):
        subsequences.append(seq[start:])

    return subsequences


def find_positions_of_subsequence(seq, subseq, start=0, ignore_case=True):
    """
    >>> find_positions_of_subsequence('abcdef', 'cd')
    [(2, 4)]

    >>> find_positions_of_subsequence('abcdef', 'cde')
    [(2, 5)]

    >>> find_positions_of_subsequence('abcdecd', 'cd')
    [(2, 4), (5, 7)]

    >>> find_positions_of_subsequence('abcdef', 'cdefg')
    []

    >>> find_positions_of_subsequence('abcdef', 'cd', start=3)
    []
    """
    positions = []
    if ignore_case:
        subseq = subseq.lower()
        seq = seq.lower()
    while True:
        start = seq.find(subseq, start)
        if start == -1:
            break
        end = start + len(subseq)
        positions.append((start, end))
        start = end

    return positions


class OrderedEnum(Enum):
    """each value is given an order based on its position in the class definition
    Copied from https://stackoverflow.com/a/42397017
    """

    def __init__(self, *args):
        try:
            # attempt to initialize other parents in the hierarchy
            super().__init__(*args)
        except TypeError:
            # ignore -- there are no other parents
            pass
        ordered = len(self.__class__.__members__) + 1
        self._order = ordered

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self._order >= other._order
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self._order > other._order
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self._order <= other._order
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self._order < other._order
        return NotImplemented

    @classmethod
    def members(cls):
        return sorted([member for member in cls], key=lambda x: x._order)

    @classmethod
    def values(cls):
        return [member.value for member in cls.members()]


if __name__ == "__main__":
    import doctest

    doctest.testmod()
