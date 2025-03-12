from typing import Sequence

from bytelang.abc.serializer import Serializable
from bytelang.abc.serializer import Serializer
from bytelang.core.result import ErrOne
from bytelang.core.result import LogResult
from bytelang.core.result import ResultAccumulator


class StructSerializer[T: Sequence[Serializable]](Serializer[T]):
    """Объединение нескольких Serializer"""

    def unpack(self, buffer: bytes) -> LogResult[T]:
        ret = ResultAccumulator()

        offset: int = 0

        for field in self._fields:
            ret.put(field.unpack(buffer[offset:offset + field.getSize()]))
            offset += field.getSize()

        return ret.map()

    def pack(self, value: T) -> LogResult[bytes]:
        if (got := len(value)) != (expected := len(self._fields)):
            return ErrOne(f"Expected: {expected} ({self}), got {got} ({value}")

        ret = ResultAccumulator()

        for field, field_value in zip(self._fields, value):
            ret.put(field.pack(field_value))

        return ret.map(lambda packed_fields: b"".join(packed_fields))

    def __init__(self, fields: Sequence[Serializer]) -> None:
        self._fields = fields

    def getSize(self) -> int:
        return sum(f.getSize() for f in self._fields)

    def __repr__(self) -> str:
        return f"{{{', '.join(map(str, self._fields))}}}"


def _test():
    from bytelang.impl.serializer.primitive import u8
    from rustpy.exceptions import Panic

    from bytelang.impl.serializer.primitive import i64
    from bytelang.impl.serializer.primitive import f64
    struct_packer: StructSerializer[tuple[int, float, tuple[int, int]]] = StructSerializer((
        u8,
        f64,
        StructSerializer((
            u8,
            i64
        ))
    ))

    try:
        print(struct_packer, struct_packer.getSize())
        b = struct_packer.pack((100, 0.4 - 0.1, (10, 100))).unwrap()
        print(tuple(b))
        print(struct_packer.unpack(b).unwrap())

    except Panic as e:
        print(e)

    pass


if __name__ == '__main__':
    _test()
