"""Общеиспользуемые узлы АСД (Package, Source)"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable

from bytelang.abc.parser import Parser
from bytelang.core.rvalue import RValueSpec
from bytelang.core.tokens import Operator
from bytelang.core.tokens import TokenType
from bytelang.impl.node.super import SuperNode
from bytelang.impl.semantizer.common import CommonSemanticContext
from rustpy.result import MultipleErrorsResult
from rustpy.result import Result
from rustpy.result import SingleResult


class Expression(SuperNode[CommonSemanticContext, RValueSpec, "Expression"], ABC):
    """Выражение"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Expression, Iterable[str]]:
        match parser.tokens.peek().type:
            case TokenType.Identifier:
                return Identifier.parse(parser)

            case TokenType.Macro:
                return MacroCall.parse(parser)

            case literal_token if literal_token.isLiteral():
                return Literal.parse(parser)

            case not_expression_token:
                return SingleResult.error((f"Token not an expression: {not_expression_token}",))

    @abstractmethod
    def accept(self, context: CommonSemanticContext) -> Result[RValueSpec, Iterable[str]]:
        pass


@dataclass(frozen=True)
class Identifier(Expression):
    """Узел Идентификатора"""

    id: str
    """Имя"""

    def accept(self, context: CommonSemanticContext) -> Result[RValueSpec, Iterable[str]]:
        return SingleResult.fromOptional(context.const_registry.get(self.id), lambda: (f"Const not found: {self}",))

    @classmethod
    def parse(cls, parser: Parser) -> Result[Identifier, Iterable[str]]:
        """Парсинг токена в узел Идентификатора"""
        return parser.consume(TokenType.Identifier).map(lambda ok: cls(ok.value), lambda e: (e,))


@dataclass(frozen=True)
class Literal(Expression):
    """Узел Литерала"""

    value: RValueSpec
    """Значение"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Literal, Iterable[str]]:
        """Парсинг токена в узел Литерала"""
        ret = MultipleErrorsResult()
        token = parser.tokens.next()

        if (rv_maker := token.type.getRightValueMaker()) is None:
            ret.putOptionalError(f"Ожидался литерал, получено: {token}")

        return ret.make(lambda: cls(rv_maker(token.value)))

    def accept(self, context: CommonSemanticContext) -> Result[RValueSpec, Iterable[str]]:
        return SingleResult.ok(self.value)


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

    def accept(self, context: CommonSemanticContext) -> Result[RValueSpec, Iterable[str]]:
        if (rv := self.operand.accept(context)).isError():
            return rv

        return rv.unwrap().applyUnaryOperator(self.op).map(err=lambda e: (e,))


@dataclass(frozen=True)
class BinaryOp(Expression):
    """Узел Бинарной операции"""

    op: Operator
    """Оператор"""
    left: Expression
    """Левый операнд"""
    right: Expression
    """Правый операнд"""

    def accept(self, context: CommonSemanticContext) -> Result[RValueSpec, Iterable[str]]:
        ret = MultipleErrorsResult()

        a = ret.putMulti(self.left.accept(context))
        b = ret.putMulti(self.right.accept(context))

        if ret.isError():
            return ret.flow()

        c = ret.putMulti(a.unwrap().applyBinaryOperator(b.unwrap(), self.op))

        return ret.make(lambda: c.unwrap())


@dataclass(frozen=True)
class MacroCall(Expression):
    """Узел развёртки макроса"""

    id: Identifier
    """Идентификатор макроса"""
    args: Iterable[Expression]
    """Аргументы развертки"""

    def accept(self, context: CommonSemanticContext) -> Result[RValueSpec, Iterable[str]]:
        macro = context.macro_registry.get(self.id)

        if macro is None:
            return SingleResult.error((f"macro not existing: {self}",))

        # TODO доделать развертку макроса

    @classmethod
    def parse(cls, parser: Parser) -> Result[MacroCall, Iterable[str]]:
        ret = MultipleErrorsResult()

        _id = ret.putSingle(parser.consume(TokenType.Macro))
        args = ret.putMulti(parser.braceArguments(lambda: Expression.parse(parser), TokenType.OpenRound, TokenType.CloseRound))

        return ret.make(lambda: cls(_id.unwrap().value, args.unwrap()))
