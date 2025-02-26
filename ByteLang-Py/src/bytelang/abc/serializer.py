import struct
from abc import ABC
from abc import abstractmethod

_Ser_primitive = int | float | bool
_Ser_struct = tuple[_Ser_primitive, ...]
Serializable = _Ser_primitive | _Ser_struct
"""Serializable тип"""


class Serializer[T: Serializable](ABC):
    """Serializer - упаковка, распаковка данных"""

    def __init__(self, _format: str) -> None:
        self._struct = struct.Struct(f"<{_format}")

    @abstractmethod
    def pack(self, value: T) -> bytes:
        """Упаковать значение в соответсвующее байтовое представление"""

    @abstractmethod
    def unpack(self, buffer: bytes) -> T:
        """Получить значение из соответствующего байтового представления"""

    def getSize(self) -> int:
        """Получить размер данных в байтах"""
        return self._struct.size

    def getFormat(self) -> str:
        """Получить спецификатор формата"""
        return self._struct.format.strip("<>")
