"""Общеиспользуемые узлы АСД (Package, Source)"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable
from typing import Optional

from bytelang.abc.node import Directive
from bytelang.abc.node import Expression
from bytelang.abc.node import Node
from bytelang.abc.parser import Parser
from bytelang.core.stream import Stream
from bytelang.core.tokens import Operator
from bytelang.core.tokens import Token
from bytelang.core.tokens import TokenType
from rustpy.result import Result


class ParsableDirective(Directive, ABC):
    """Директива, поддерживающая парсинг из токенов"""

    @classmethod
    @abstractmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        """Преобразовать токены в конкретную директиву"""


@dataclass(frozen=True)
class ConstDeclareDirective(ParsableDirective):
    """Объявление константного значения"""

    id: Identifier
    """Идентификатор константы"""
    expression: Expression
    """Выражение значения"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        _id = Identifier.parse(parser.tokens)

        if _id.isError():
            return Result.error(_id.getError())

        result = parser.expression()

        if result.isError():
            return Result.error(result.getError())

        return Result.ok(cls(_id.unwrap(), result.unwrap()))


@dataclass(frozen=True)
class Identifier(Expression):
    """Узел Идентификатора"""

    id: str
    """Имя"""

    @classmethod
    def parse(cls, stream: Stream[Token]) -> Result[Identifier, str]:
        """Парсинг токена в узел Идентификатора"""
        token = stream.next()

        if token.type == TokenType.Identifier:
            return Result.ok(cls(token.value))

        return Result.error(f"Ожидался идентификатор, получено: {token}")


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


@dataclass(frozen=True)
class Literal[T: (int, float, str)](Expression):
    """Узел Литерала"""

    value: T
    """Значение"""

    @classmethod
    def parse(cls, stream: Stream[Token]) -> Result[Literal, str]:
        """Парсинг токена в узел Литерала"""
        token = stream.next()

        if token.type.isLiteral():
            return Result.ok(cls(token.value))

        return Result.error(f"Ожидался литерал, получено: {token}")


@dataclass(frozen=True)
class UnaryOp(Expression):
    """Узел Префиксной Унарной операции"""

    op: Operator
    """Оператор"""
    operand: Expression
    """Операнд"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[UnaryOp, Iterable[str]]:
        """Создать узел Префиксной Унарной операции"""

        token = parser.tokens.next()

        if (operator := token.type.asOperator()) is None:
            return Result.error((f"Ожидался оператор, получено: {token}",))

        result = parser.expression()

        if result.isError():
            return Result.error(result.getError())

        return Result.ok(cls(operator, result.unwrap()))


@dataclass(frozen=True)
class BinaryOp(Expression):
    """Узел Бинарной операции"""

    op: Operator
    """Оператор"""
    left: Expression
    """Левый операнд"""
    right: Expression
    """Правый операнд"""
