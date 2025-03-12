import struct
from itertools import chain
# noinspection PyPep8Naming
from struct import error as StructError
from typing import Callable
from typing import Final
from typing import Iterable

from bytelang.abc.serializer import Serializer
from bytelang.core.result import ErrOne
from bytelang.core.result import LogResult
from bytelang.core.result import Ok


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


class PrimitiveSerializer[T: (int, float)](Serializer[T]):
    """Примитивные типы"""

    type Value = T

    def __init__(self, _format: str) -> None:
        self._struct = struct.Struct(f"<{_format}")

    def getSize(self) -> int:
        return self._struct.size

    def unpack(self, buffer: bytes) -> LogResult[T]:
        return self._structResultWrapper(buffer, lambda _b: self._struct.unpack(_b)[0])

    def pack(self, value: T) -> LogResult[bytes]:
        return self._structResultWrapper(value, self._struct.pack)

    def __repr__(self) -> str:
        return f"{_Format.matchPrefix(self._struct.format.strip("<>"))}{self.getSize() * 8}"

    @staticmethod
    def _structResultWrapper[F, T](_from: F, from_to_func: Callable[[F], T]) -> LogResult[T]:
        try:
            _to = from_to_func(_from)

        except StructError as e:
            return ErrOne(f"Primitive error: {e} ({_from})")

        else:
            return Ok(_to)


u8 = PrimitiveSerializer[int | bool](_Format.U8)
u16 = PrimitiveSerializer[int](_Format.U16)
u32 = PrimitiveSerializer[int](_Format.U32)
u64 = PrimitiveSerializer[int](_Format.U64)

i8 = PrimitiveSerializer[int](_Format.I8)
i16 = PrimitiveSerializer[int](_Format.I16)
i32 = PrimitiveSerializer[int](_Format.I32)
i64 = PrimitiveSerializer[int](_Format.I64)

f32 = PrimitiveSerializer[float](_Format.F32)
f64 = PrimitiveSerializer[float](_Format.F64)
