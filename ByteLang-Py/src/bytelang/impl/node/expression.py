"""Общеиспользуемые узлы АСД (Package, Source)"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Iterable

from bytelang.abc.parser import Parser
from bytelang.abc.semantic import SemanticContext
from bytelang.core.tokens import Operator
from bytelang.core.tokens import TokenType
from bytelang.impl.node.super import SuperNode
from rustpy.result import MultipleErrorsResult
from rustpy.result import Result
from rustpy.result import SingleResult


class Expression[S: SemanticContext](SuperNode[S, "Expression", "Expression"], ABC):
    """Выражение"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Expression, Iterable[str]]:
        match parser.tokens.peek().type:
            case TokenType.Identifier:
                return Identifier.parse(parser)

            case TokenType.Macro:
                return Macro.parse(parser)

            case literal_token if literal_token.isLiteral():
                return Literal.parse(parser)

            case not_expression_token:
                return SingleResult.error((f"Token not an expression: {not_expression_token}",))


@dataclass(frozen=True)
class Identifier(Expression):
    """Узел Идентификатора"""

    id: str
    """Имя"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Identifier, Iterable[str]]:
        """Парсинг токена в узел Идентификатора"""
        return parser.consume(TokenType.Identifier).map(lambda ok: cls(ok.value), lambda e: (e,))


@dataclass(frozen=True)
class Literal[T: (int, float, str)](Expression):
    """Узел Литерала"""

    value: T
    """Значение"""

    def accept(self, semantizer: T) -> Result[Expression, Iterable[str]]:
        return SingleResult.ok(self)

    @classmethod
    def parse(cls, parser: Parser) -> Result[Literal, Iterable[str]]:
        """Парсинг токена в узел Литерала"""
        ret = MultipleErrorsResult()

        token = parser.tokens.next()

        if not token.type.isLiteral():
            ret.putError(f"Ожидался литерал, получено: {token}")

        return ret.make(lambda: cls(token.value))


@dataclass(frozen=True)
class UnaryOp(Expression):
    """Узел Префиксной Унарной операции"""

    op: Operator
    """Оператор"""
    operand: Expression
    """Операнд"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[UnaryOp, Iterable[str]]:
        token = parser.tokens.next()

        if (operator := token.type.asOperator()) is None:
            return SingleResult.error((f"Ожидался оператор, получено: {token}",))

        return Expression.parse(parser).map(lambda expr: cls(operator, expr))


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
class Macro(Expression):
    """Узел развёртки макроса"""

    id: Identifier
    """Идентификатор макроса"""
    args: Iterable[Expression]
    """Аргументы развертки"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Macro, Iterable[str]]:
        ret = MultipleErrorsResult()

        _id = ret.putSingle(parser.consume(TokenType.Macro))
        args = ret.putMulti(parser.braceArguments(lambda: Expression.parse(parser), TokenType.OpenRound, TokenType.CloseRound))

        return ret.make(lambda: cls(_id.unwrap().value, args.unwrap()))
