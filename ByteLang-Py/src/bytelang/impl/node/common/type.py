from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from bytelang.abc.node import Expression
from bytelang.abc.node import Node
from bytelang.core.stream import Stream
from bytelang.core.tokens import Token
from bytelang.core.tokens import TokenType
from bytelang.impl.node.common.expression import Identifier
from rustpy.result import Result


class Type(Node):
    """Узел типа"""


@dataclass(frozen=True)
class PureType(Type):
    """Чистый тип"""

    id: Identifier
    """Идентификатор типа"""

    @classmethod
    def parse(cls, stream: Stream) -> Result[Type, str]:
        """Создать чистый тип на основе идентификатора"""
        type_id = Identifier.parse(stream)

        if type_id.isError():
            return Result.error(type_id.getError())

        return Result.ok(cls(type_id.unwrap()))


@dataclass(frozen=True)
class PointerType(Type):
    """Тип Указателя"""

    pointer: Type
    """Тип указателя"""


@dataclass(frozen=True)
class ArrayType(Type):
    """Тип Массив"""

    type: Type
    """Тип элементов массива"""
    length: Optional[Expression]
    """
    Выражение, определяющее длину массива
    (None - размер массива определяется на основании инициализатора)
    """


@dataclass(frozen=True)
class Field(Node):
    """Узел объявления поля"""

    name: Identifier
    """Наименование поля"""
    type: Type
    """Тип поля"""

    @classmethod
    def parse(cls, stream: Stream[Token]) -> Result[Field, str]:
        """Парсинг токенов в поле"""

        if (name := Identifier.parse(stream)).isError():
            return Result.error(name.getError())

        if (token := stream.next()).type != TokenType.Colon:
            return Result.error(f"Invalid token: {token}")

        if (_type := PureType.parse(stream)).isError():
            return Result.error(_type.getError())

        return Result.ok(cls(name.unwrap(), _type.unwrap()))
