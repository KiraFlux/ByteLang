from typing import Iterable

from bytelang.impl.registry.immediate import ImmediateRegistry
from bytelang.impl.serializer.primitive import PrimitiveSerializer
from bytelang.impl.serializer.primitive import f32
from bytelang.impl.serializer.primitive import f64
from bytelang.impl.serializer.primitive import i16
from bytelang.impl.serializer.primitive import i32
from bytelang.impl.serializer.primitive import i64
from bytelang.impl.serializer.primitive import i8
from bytelang.impl.serializer.primitive import u16
from bytelang.impl.serializer.primitive import u32
from bytelang.impl.serializer.primitive import u64
from bytelang.impl.serializer.primitive import u8


class PrimitiveRegistry(ImmediateRegistry[str, PrimitiveSerializer]):

    def __init__(self) -> None:
        super().__init__(self._getItems())

    @staticmethod
    def _getPrimitives() -> Iterable[PrimitiveSerializer]:
        return i8, u8, i16, u16, i32, u32, i64, u64, f32, f64

    def _getItems(self) -> Iterable[tuple[str, PrimitiveSerializer]]:
        return ((p.__str__(), p) for p in self._getPrimitives())


def _test():
    r = PrimitiveRegistry()
    print("\n".join(map(str, r.getItems())))


if __name__ == '__main__':
    _test()
