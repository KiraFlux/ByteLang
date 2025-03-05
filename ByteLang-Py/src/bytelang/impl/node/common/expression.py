"""Общеиспользуемые узлы АСД (Package, Source)"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from typing import Sequence

from bytelang.abc.node import Expression
from bytelang.abc.parser import Parsable
from bytelang.abc.parser import Parser
from bytelang.core.tokens import Operator
from bytelang.core.tokens import TokenType
from rustpy.result import Result


@dataclass(frozen=True)
class Identifier(Expression, Parsable[Expression]):
    """Узел Идентификатора"""

    id: str
    """Имя"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Identifier, Iterable[str]]:
        """Парсинг токена в узел Идентификатора"""
        token = parser.consume(TokenType.Identifier)

        if token.isOk():
            return Result.ok(cls(token.unwrap().value))

        return Result.error((token.getError(),))


@dataclass(frozen=True)
class Literal[T: (int, float, str)](Expression, Parsable[Expression]):
    """Узел Литерала"""

    value: T
    """Значение"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Literal, Iterable[str]]:
        """Парсинг токена в узел Литерала"""
        token = parser.tokens.next()

        if not token.type.isLiteral():
            return Result.error((f"Ожидался литерал, получено: {token}",))

        return Result.ok(cls(token.value))


@dataclass(frozen=True)
class UnaryOp(Expression, Parsable[Expression]):
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


@dataclass(frozen=True)
class Macro(Expression, Parsable[Expression]):
    """Узел развёртки макроса"""

    id: Identifier
    """Идентификатор макроса"""
    args: Sequence[Expression]
    """Аргументы развертки"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Macro, Iterable[str]]:
        _id = parser.consume(TokenType.Macro)

        if _id.isError():
            return Result.error(_id.getError())

        args = parser.braceArguments(parser.expression, TokenType.OpenRound, TokenType.CloseRound)

        if args.isError():
            return Result.error(args.getError())

        return Result.ok(cls(Identifier(_id.unwrap().value), args.unwrap()))
