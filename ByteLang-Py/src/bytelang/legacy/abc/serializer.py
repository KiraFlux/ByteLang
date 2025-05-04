from abc import ABC
from abc import abstractmethod
from typing import Sequence

from bytelang.legacy.core.result import LogResult

type _serializable = int | float
type _serializable = Sequence[_serializable] | _serializable
type _serializable = Sequence[_serializable] | _serializable

Serializable = _serializable


class Serializer[T: Serializable](ABC):
    """Serializer - упаковка, распаковка данных"""

    @abstractmethod
    def pack(self, value: T) -> LogResult[bytes]:
        """Упаковать значение в соответсвующее байтовое представление"""

    @abstractmethod
    def unpack(self, buffer: bytes) -> LogResult[T]:
        """Получить значение из соответствующего байтового представления"""

    @abstractmethod
    def getSize(self) -> int:
        """Получить размер данных в байтах"""
