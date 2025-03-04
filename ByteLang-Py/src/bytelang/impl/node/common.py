"""Общеиспользуемые узлы АСД (Package, Source)"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable

from bytelang.abc.node import Directive
from bytelang.abc.node import Expression
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

    expression: Expression
    """Выражение значения"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        result = parser.expression()

        if result.isError():
            return Result.error(result.getError())

        return Result.ok(cls(result.unwrap()))


@dataclass(frozen=True)
class Identifier(Expression):
    """Узел Идентификатора"""

    name: str
    """Имя"""

    @classmethod
    def parse(cls, stream: Stream[Token]) -> Result[Identifier, str]:
        """Парсинг токена в узел Идентификатора"""
        token = stream.next()

        if token.type == TokenType.Identifier:
            return Result.ok(cls(token.value))

        return Result.error(f"Ожидался идентификатор, получено: {token}")


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
