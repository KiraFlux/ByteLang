from math import log10
from math import ceil


def digitsLength(n: int) -> int:
    if n < 0:
        raise NotImplementedError

    if n < 2:
        return 1

    return ceil(log10(n))
