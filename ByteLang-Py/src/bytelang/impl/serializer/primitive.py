from itertools import chain
from typing import Final
from typing import Iterable

from bytelang.abc.serializer import Serializer


class _Format:
    I8: Final[str] = "b"
    I16: Final[str] = "h"
    I32: Final[str] = "l"
    I64: Final[str] = "q"

    U8: Final[str] = "B"
    U16: Final[str] = "H"
    U32: Final[str] = "L"
    U64: Final[str] = "Q"

    F32: Final[str] = "f"
    F64: Final[str] = "d"

    @classmethod
    def getSigned(cls) -> Iterable[str]:
        """Все знаковые форматы"""
        return cls.I8, cls.I16, cls.I32, cls.I64

    @classmethod
    def getUnsigned(cls) -> Iterable[str]:
        """Все форматы без знака"""
        return cls.U8, cls.U16, cls.U32, cls.U64

    @classmethod
    def getExponential(cls) -> Iterable[str]:
        """Все экспоненциальные форматы"""
        return cls.F32, cls.F64

    @classmethod
    def getAll(cls) -> Iterable[str]:
        """Все типы"""
        return chain(cls.getExponential(), cls.getSigned(), cls.getUnsigned())

    @classmethod
    def matchPrefix(cls, fmt: str) -> str:
        """Подобрать префикс"""
        match fmt:
            case _ if fmt in cls.getExponential():
                return "f"

            case _ if fmt in cls.getSigned():
                return "i"

            case _ if fmt in cls.getUnsigned():
                return "u"

        raise ValueError(fmt)


class Primitive[T](Serializer[T]):
    """Примитивные типы"""

    def pack(self, value: T) -> bytes:
        return self._struct.pack(value)

    def unpack(self, buffer: bytes) -> T:
        return self._struct.unpack(buffer)[0]

    def __str__(self) -> str:
        return f"{_Format.matchPrefix(self.getFormat())}{self.getSize() * 8}"


u8 = Primitive[int | bool](_Format.U8)
u16 = Primitive[int](_Format.U16)
u32 = Primitive[int](_Format.U32)
u64 = Primitive[int](_Format.U64)

i8 = Primitive[int](_Format.I8)
i16 = Primitive[int](_Format.I16)
i32 = Primitive[int](_Format.I32)
i64 = Primitive[int](_Format.I64)

f32 = Primitive[float](_Format.F32)
f64 = Primitive[float](_Format.F64)
