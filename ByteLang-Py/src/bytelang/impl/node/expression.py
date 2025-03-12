"""Общеиспользуемые узлы АСД (Package, Source)"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable
from typing import Mapping
from typing import Optional

from bytelang.abc.parser import Parser
from bytelang.abc.profiles import RValueProfile
from bytelang.abc.registry import Registry
from bytelang.core.ops import Operator
from bytelang.core.result import ErrOne
from bytelang.core.result import LogResult
from bytelang.core.result import Ok
from bytelang.core.result import ResultAccumulator
from bytelang.core.tokens import TokenType
from bytelang.impl.node.super import SuperNode
from bytelang.impl.semantizer.common import CommonSemanticContext


class Expression(SuperNode[CommonSemanticContext, RValueProfile, "Expression"], ABC):
    """Выражение"""

    @classmethod
    def parse(cls, parser: Parser) -> LogResult[Expression]:
        match parser.tokens.peek().type:
            case TokenType.Identifier:
                return Identifier.parse(parser)

            case TokenType.MacroCall:
                return MacroCall.parse(parser)

            case literal_token if literal_token.isLiteral():
                return Literal.parse(parser)

            case not_expression_token:
                return ErrOne(f"Token not an expression: {not_expression_token}")

    @abstractmethod
    def accept(self, context: CommonSemanticContext) -> LogResult[RValueProfile]:
        pass

    @abstractmethod
    def expand(self, table: Mapping[Identifier, Expression]) -> Expression:
        """Развернуть макрос"""


@dataclass(frozen=True)
class Identifier(Expression):
    """Узел Идентификатора"""

    id: str
    """Имя"""

    def expand(self, table: Mapping[Identifier, Expression]) -> Expression:
        return table.get(self, self)

    def accept(self, context: CommonSemanticContext) -> LogResult[RValueProfile]:
        return context.const_registry.get(self.id)

    @classmethod
    def parse(cls, parser: Parser) -> LogResult[Identifier]:
        """Парсинг токена в узел Идентификатора"""
        return parser.consume(TokenType.Identifier).map(lambda ok: cls(ok.value))


@dataclass(frozen=True)
class Literal[T](Expression):
    """Узел Литерала"""

    value: RValueProfile[T]
    """Значение"""

    def expand(self, table: Mapping[Identifier, Expression]) -> Expression:
        return self

    @classmethod
    def parse(cls, parser: Parser) -> LogResult[Literal[T]]:
        """Парсинг токена в узел Литерала"""
        ret = ResultAccumulator()
        token = parser.tokens.next()

        if (rv_maker := token.type.getRightValueMaker()) is None:
            ret.put(ErrOne(f"Ожидался литерал, получено: {token}"))

        return ret.map(lambda _: cls(rv_maker(token.value)))

    def accept(self, context: CommonSemanticContext) -> LogResult[RValueProfile[T]]:
        return Ok(self.value)


@dataclass(frozen=True)
class UnaryOp(Expression):
    """Узел Префиксной Унарной операции"""

    op: Operator
    """Оператор"""
    operand: Expression
    """Операнд"""

    def expand(self, table: Mapping[Identifier, Expression]) -> Expression:
        return UnaryOp(self.op, self.operand.expand(table))

    @classmethod
    def parse(cls, parser: Parser) -> LogResult[UnaryOp]:
        token = parser.tokens.next()

        if (operator := token.type.asOperator()) is None:
            return ErrOne(f"Ожидался оператор, получено: {token}")

        return Expression.parse(parser).map(lambda expr: cls(operator, expr))

    def accept[T](self, context: CommonSemanticContext) -> LogResult[RValueProfile[T]]:
        return self.operand.accept(context).andThen(lambda rv: rv.applyUnaryOperator(self.op))


@dataclass(frozen=True)
class BinaryOp(Expression):
    """Узел Бинарной операции"""

    op: Operator
    """Оператор"""
    left: Expression
    """Левый операнд"""
    right: Expression
    """Правый операнд"""

    def expand(self, table: Mapping[Identifier, Expression]) -> Expression:
        return BinaryOp(self.op, self.left.expand(table), self.right.expand(table))

    def accept(self, context: CommonSemanticContext) -> LogResult[RValueProfile]:
        ret = ResultAccumulator()

        a = ret.put(self.left.accept(context))
        b = ret.put(self.right.accept(context))

        if ret.isErr():
            return ret.map()

        c = ret.put(a.unwrap().applyBinaryOperator(b.unwrap(), self.op))

        return ret.map(lambda _: c.unwrap())


@dataclass(frozen=True)
class HasIdentifier:
    """Узел имеет идентификатор"""

    identifier: Identifier
    """Идентификатор узла"""


class HasExistingID(HasIdentifier):
    """Узел имеет идентификатор, уже содержащийся в реестре"""


class HasUniqueID(HasIdentifier):
    """Узел имеет уникальный идентификатор"""

    def checkIdentifier[T](self, registry: Registry[str, T]) -> Optional[str]:
        """Проверить уникальность идентификатора"""
        if registry.has(self.identifier.id):
            return f"{registry} has {self}"


@dataclass(frozen=True)
class MacroCall(Expression):
    """Узел развёртки макроса"""

    macro_id: str
    arguments: Iterable[Expression]

    def expand(self, table: Mapping[Identifier, Expression]) -> Expression:
        return MacroCall(self.macro_id, tuple(arg.expand(table) for arg in self.arguments))

    def accept(self, context: CommonSemanticContext) -> LogResult[RValueProfile]:
        return (
            context.macro_registry.get(self.macro_id)
            .andThen(lambda macro: macro.expand(tuple(self.arguments)))
            .andThen(lambda expand: expand.accept(context))
        )

    @classmethod
    def parse(cls, parser: Parser) -> LogResult[MacroCall]:
        ret = ResultAccumulator()

        _id = ret.put(parser.consume(TokenType.MacroCall))
        args = ret.put(parser.braceArguments(lambda: Expression.parse(parser), TokenType.OpenRound, TokenType.CloseRound))

        return ret.map(lambda _: cls(_id.unwrap().value, args.unwrap()))
