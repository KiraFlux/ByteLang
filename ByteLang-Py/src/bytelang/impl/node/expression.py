"""Общеиспользуемые узлы АСД (Package, Source)"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable
from typing import Mapping
from typing import Optional
from typing import Sequence

from bytelang.abc.parser import Parser
from bytelang.abc.registry import Registry
from bytelang.core.ops import Operator
from bytelang.core.profile.macro import MacroProfile
from bytelang.core.profile.rvalue import RValueProfile
from bytelang.core.result import MultipleErrorsResult
from bytelang.core.result import Result
from bytelang.core.result import SingleResult
from bytelang.core.tokens import TokenType
from bytelang.impl.node.super import SuperNode
from bytelang.impl.semantizer.common import CommonSemanticContext


class Expression(SuperNode[CommonSemanticContext, RValueProfile, "Expression"], ABC):
    """Выражение"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Expression, Iterable[str]]:
        match parser.tokens.peek().type:
            case TokenType.Identifier:
                return Identifier.parse(parser)

            case TokenType.MacroCall:
                return MacroCall.parse(parser)

            case literal_token if literal_token.isLiteral():
                return Literal.parse(parser)

            case not_expression_token:
                return SingleResult.error((f"Token not an expression: {not_expression_token}",))

    @abstractmethod
    def accept(self, context: CommonSemanticContext) -> Result[RValueProfile, Iterable[str]]:
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

    def accept(self, context: CommonSemanticContext) -> Result[RValueProfile, Iterable[str]]:
        return SingleResult.fromOptional(context.const_registry.get(self.id), lambda: (f"Const not found: {self}",))

    @classmethod
    def parse(cls, parser: Parser) -> Result[Identifier, Iterable[str]]:
        """Парсинг токена в узел Идентификатора"""
        return parser.consume(TokenType.Identifier).map(lambda ok: cls(ok.value), lambda e: (e,))


@dataclass(frozen=True)
class MacroProfileImpl(MacroProfile[Expression]):
    """Реализация профиля макроса"""

    arguments: Sequence[Identifier]
    template: Expression

    def expand(self, arguments: Sequence[Expression]) -> Result[Expression, str]:
        if (len_got := len(arguments)) != (len_expected := len(self.arguments)):
            return SingleResult.error(f"Expected: {len_expected} ({self.arguments}), got: {len_got} ({arguments})")

        return SingleResult.ok(self.template.expand({key: expr for key, expr in zip(self.arguments, arguments)}))


@dataclass(frozen=True)
class Literal(Expression):
    """Узел Литерала"""

    value: RValueProfile
    """Значение"""

    def expand(self, table: Mapping[Identifier, Expression]) -> Expression:
        return self

    @classmethod
    def parse(cls, parser: Parser) -> Result[Literal, Iterable[str]]:
        """Парсинг токена в узел Литерала"""
        ret = MultipleErrorsResult()
        token = parser.tokens.next()

        if (rv_maker := token.type.getRightValueMaker()) is None:
            ret.putOptionalError(f"Ожидался литерал, получено: {token}")

        return ret.make(lambda: cls(rv_maker(token.value)))

    def accept(self, context: CommonSemanticContext) -> Result[RValueProfile, Iterable[str]]:
        return SingleResult.ok(self.value)


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
    def parse(cls, parser: Parser) -> Result[UnaryOp, Iterable[str]]:
        token = parser.tokens.next()

        if (operator := token.type.asOperator()) is None:
            return SingleResult.error((f"Ожидался оператор, получено: {token}",))

        return Expression.parse(parser).map(lambda expr: cls(operator, expr))

    def accept(self, context: CommonSemanticContext) -> Result[RValueProfile, Iterable[str]]:
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

    def expand(self, table: Mapping[Identifier, Expression]) -> Expression:
        return BinaryOp(self.op, self.left.expand(table), self.right.expand(table))

    def accept(self, context: CommonSemanticContext) -> Result[RValueProfile, Iterable[str]]:
        ret = MultipleErrorsResult()

        a = ret.putMulti(self.left.accept(context))
        b = ret.putMulti(self.right.accept(context))

        if ret.isError():
            return ret.flow()

        c = ret.putSingle(a.unwrap().applyBinaryOperator(b.unwrap(), self.op))

        return ret.make(lambda: c.unwrap())


@dataclass(frozen=True)
class HasIdentifier:
    """Узел имеет идентификатор"""

    identifier: Identifier
    """Идентификатор узла"""


class HasExistingID(HasIdentifier):
    """Узел имеет идентификатор, уже содержащийся в реестре"""

    def checkIdentifier[T](self, registry: Registry[str, T]) -> Result[T, str]:
        """Проверить наличие идентификатора и получить результат"""
        return SingleResult.fromOptional(registry.get(self.identifier.id), lambda: f"ID{self} not existing in {registry}")


class HasUniqueID(HasIdentifier):
    """Узел имеет уникальный идентификатор"""

    def checkIdentifier[T](self, registry: Registry[str, T]) -> Optional[str]:
        """Проверить уникальность идентификатора"""
        if registry.has(self.identifier.id):
            return f"{registry} has {self}"


@dataclass(frozen=True)
class MacroCall(Expression, HasExistingID):
    """Узел развёртки макроса"""

    arguments: Iterable[Expression]

    def expand(self, table: Mapping[Identifier, Expression]) -> Expression:
        return MacroCall(self.identifier, (arg.expand(table) for arg in self.arguments))

    def accept(self, context: CommonSemanticContext) -> Result[RValueProfile, Iterable[str]]:
        macro_result = self.checkIdentifier(context.macro_registry)

        if macro_result.isError():
            return macro_result.flow(lambda e: (e,))

        expand: Result[Expression, str] = macro_result.unwrap().expand(self.arguments)

        if expand.isError():
            return expand.flow(lambda e: (e,))

        return expand.unwrap().accept(context)

    @classmethod
    def parse(cls, parser: Parser) -> Result[MacroCall, Iterable[str]]:
        ret = MultipleErrorsResult()

        _id = ret.putSingle(parser.consume(TokenType.MacroCall))
        args = ret.putMulti(parser.braceArguments(lambda: Expression.parse(parser), TokenType.OpenRound, TokenType.CloseRound))

        return ret.make(lambda: cls(_id.unwrap().value, args.unwrap()))
