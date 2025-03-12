from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from typing import Sequence

from bytelang.abc.serializer import Serializable
from bytelang.abc.serializer import Serializer
from bytelang.core.LEGACY_result import LEGACY_Result
from bytelang.core.LEGACY_result import LEGACYResultAccumulator
from bytelang.core.LEGACY_result import SingleLEGACYResult


@dataclass(frozen=True)
class ArraySerializer[T: Serializable](Serializer[Sequence[T]]):
    """Сериализатор однородной структуры (Массив)"""

    _item_serializer: Serializer[T]
    """Сериализатор элемента массива"""
    _length: int
    """Длинна массива"""

    @classmethod
    def new(cls, item: Serializer[T], length: int) -> LEGACY_Result[ArraySerializer, str]:
        """Создать массив с проверкой"""
        if length < 1:
            return SingleLEGACYResult.error(f"Array len not valid: {length}")
        return SingleLEGACYResult.ok(cls(item, length))

    def unpack(self, buffer: bytes) -> LEGACY_Result[T, Iterable[str]]:
        ret = LEGACYResultAccumulator()

        offset: int = 0

        for _ in range(self._length):
            ret.putMulti(self._item_serializer.unpack(buffer[offset:offset + self._item_serializer.getSize()]))
            offset += self._item_serializer.getSize()

        return ret.map()

    def pack(self, value: T) -> LEGACY_Result[bytes, Iterable[str]]:
        if (got := len(value)) != self._length:
            return SingleLEGACYResult.error((f"Expected: {self._length} ({self}), got {got} ({value}",))

        ret = LEGACYResultAccumulator()

        for field_value in value:
            ret.putMulti(self._item_serializer.pack(field_value))

        return ret.map(lambda packed_fields: b"".join(packed_fields))

    def getSize(self) -> int:
        return self._item_serializer.getSize() * self._length

    def __repr__(self) -> str:
        return f"[{self._length}]{self._item_serializer}"


def _test():
    from bytelang.impl.serializer.primitive import u8
    array = ArraySerializer.new(u8, 64).unwrap()

    print(f"{array=} {array.getSize()=}")

    pass


if __name__ == '__main__':
    _test()
