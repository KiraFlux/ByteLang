"""Streams"""
from abc import ABC
from abc import abstractmethod
from typing import Iterable
from typing import Optional
from typing import Sequence


class InputStream[T](ABC):
    """Поток входа (для записи)"""

    @abstractmethod
    def put(self, item: T) -> None:
        """Поместить элемент"""

    @abstractmethod
    def extend(self, items: Iterable[T]) -> None:
        """Добавить элементы"""

    @abstractmethod
    def getItems(self) -> Sequence[T]:
        """Получить последовательность элементов"""


class OutputStream[T](ABC):
    """Поток вывода (для чтения)"""

    @abstractmethod
    def peek(self) -> Optional[T]:
        """Получить последнее значение"""

    @abstractmethod
    def next(self) -> Optional[T]:
        """Получить следующий элемент"""
