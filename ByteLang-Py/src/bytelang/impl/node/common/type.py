from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from typing import Optional

from bytelang.abc.node import Expression
from bytelang.abc.node import Node
from bytelang.abc.parser import Parsable
from bytelang.abc.parser import Parser
from bytelang.core.tokens import TokenType
from bytelang.impl.node.common.expression import Identifier
from rustpy.result import Result


class Type(Node):
    """Узел типа"""


@dataclass(frozen=True)
class PureType(Type, Parsable[Type]):
    """Чистый тип"""

    id: Identifier
    """Идентификатор типа"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Type, Iterable[str]]:
        """Создать чистый тип на основе идентификатора"""
        return Identifier.parse(parser).map(lambda ok: cls(ok))


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
class Field(Node, Parsable[Node]):
    """Узел объявления поля"""

    name: Identifier
    """Наименование поля"""
    type: Type
    """Тип поля"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Field, Iterable[str]]:
        """Парсинг токенов в поле"""

        if (name := Identifier.parse(parser)).isError():
            return Result.error(name.getError())

        if (token := parser.consume(TokenType.Colon)).isError():
            return Result.error(token.getError())

        return PureType.parse(parser).map(lambda t: cls(name.unwrap(), t))
