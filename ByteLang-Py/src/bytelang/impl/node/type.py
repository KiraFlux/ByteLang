from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Iterable
from typing import Optional

from bytelang.abc.parser import Parser
from bytelang.core.tokens import TokenType
from bytelang.impl.node.expression import Expression
from bytelang.impl.node.expression import Identifier
from bytelang.impl.node.super import SuperNode
from bytelang.impl.semantizer.common import CommonSemanticContext
from rustpy.result import MultipleErrorsResult
from rustpy.result import Result


class Type(SuperNode[CommonSemanticContext, NotImplemented, 'Type'], ABC):
    """Узел типа"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Type, Iterable[str]]:
        return PureType.parse(parser)


@dataclass(frozen=True)
class PureType(Type):
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
class Field(SuperNode[CommonSemanticContext, NotImplemented, "Field"]):
    """Узел объявления поля"""

    name: Identifier
    """Наименование поля"""
    type: Type
    """Тип поля"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Field, Iterable[str]]:
        """Парсинг токенов в поле"""
        ret = MultipleErrorsResult()

        name = ret.putSingle(Identifier.parse(parser))
        ret.putSingle(parser.consume(TokenType.Colon))
        pure = ret.putMulti(PureType.parse(parser))

        return ret.make(lambda: cls(name.unwrap(), pure.unwrap()))
