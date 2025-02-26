from typing import Sequence

from bytelang.abc.serializer import Serializer
from bytelang.impl.serializer.primitive import Primitive


class Struct[T](Serializer[T]):
    """Объединение нескольких примитивов"""

    def __init__(self, fields: Sequence[Primitive]) -> None:
        super().__init__(''.join(map(lambda f: f.getFormat(), fields)))
        self._fields = fields

    def unpack(self, buffer: bytes) -> T:
        return self._struct.unpack(buffer)

    def pack(self, fields: T) -> bytes:
        return self._struct.pack(*fields)

    def __str__(self) -> str:
        return f"{{{', '.join(map(str, self._fields))}}}"
