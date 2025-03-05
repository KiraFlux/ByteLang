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
from rustpy.result import MultipleErrorsResult
from rustpy.result import Result
from rustpy.result import SingleResult


@dataclass(frozen=True)
class Identifier(Expression, Parsable[Expression]):
    """Узел Идентификатора"""

    id: str
    """Имя"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Identifier, str]:
        """Парсинг токена в узел Идентификатора"""
        return parser.consume(TokenType.Identifier).map(lambda ok: cls(ok.value))


@dataclass(frozen=True)
class Literal[T: (int, float, str)](Expression, Parsable[Expression]):
    """Узел Литерала"""

    value: T
    """Значение"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Literal, str]:
        """Парсинг токена в узел Литерала"""
        token = parser.tokens.next()

        if not token.type.isLiteral():
            return SingleResult.error(f"Ожидался литерал, получено: {token}")

        return SingleResult.ok(cls(token.value))


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
            return SingleResult.error((f"Ожидался оператор, получено: {token}",))

        return parser.expression().map(lambda expr: cls(operator, expr))


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
    args: Iterable[Expression]
    """Аргументы развертки"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Macro, Iterable[str]]:
        ret = MultipleErrorsResult()

        _id = ret.putSingle(parser.consume(TokenType.Macro))
        args = ret.putMulti(parser.braceArguments(parser.expression, TokenType.OpenRound, TokenType.CloseRound))

        return ret.make(lambda: cls(_id.unwrap().value, args.unwrap()))
