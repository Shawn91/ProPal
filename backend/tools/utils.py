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


if __name__ == "__main__":
    import doctest

    doctest.testmod()
