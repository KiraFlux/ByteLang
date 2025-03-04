"""Streams"""
from dataclasses import dataclass
from typing import Optional
from typing import Sequence


@dataclass
class Stream[T]:
    """Поток токенов"""

    _elements: Sequence[T]
    _position: int = 0

    def peek(self) -> Optional[T]:
        """Получить последнее значение"""
        if self._position < len(self._elements):
            return self._elements[self._position]

    def next(self) -> Optional[T]:
        """Получить следующий элемент"""
        ret = self.peek()
        self._position += 1
        return ret
