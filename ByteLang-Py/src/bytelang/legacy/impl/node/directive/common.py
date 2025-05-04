"""Реализации директив общего назначения"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass

from bytelang.legacy.abc.parser import Parser
from bytelang.legacy.core.result import ErrOne
from bytelang.legacy.core.result import LogResult
from bytelang.legacy.core.result import ResultAccumulator
from bytelang.legacy.core.tokens import TokenType
from bytelang.legacy.impl.node.component import HasUniqueArguments
from bytelang.legacy.impl.node.directive.super import Directive
from bytelang.legacy.impl.node.expression import Expression
from bytelang.legacy.impl.node.expression import HasUniqueID
from bytelang.legacy.impl.node.expression import Identifier
from bytelang.legacy.impl.node.type import Field
from bytelang.legacy.impl.node.type import TypeNode
from bytelang.legacy.impl.profiles.macro import MacroProfileImpl
from bytelang.legacy.impl.profiles.type import StructTypeProfile
from bytelang.legacy.impl.semantizer.common import SuperSemanticContext


class CommonDirective(Directive[SuperSemanticContext], ABC):
    """Директива общего назначения"""

    @abstractmethod
    def accept(self, context: SuperSemanticContext) -> LogResult[None]:
        pass


@dataclass(frozen=True)
class ConstDefine(CommonDirective, HasUniqueID):
    """Узел определения константного значения"""

    expression: Expression
    """Выражение значения"""

    @classmethod
    def getIdentifier(cls) -> str:
        return "const"

    def accept(self, context: SuperSemanticContext) -> LogResult[None]:
        ret = ResultAccumulator()

        maybe_already_declared = self.checkIdentifier(context.getConstants())

        if maybe_already_declared is not None:
            ret.put(ErrOne(maybe_already_declared))

        expr_value = ret.put(self.expression.accept(context))

        return ret.map(lambda _: context.getConstants().register(self.identifier.id, expr_value.unwrap()))

    @classmethod
    def parse(cls, parser: Parser) -> LogResult[Directive]:
        ret = ResultAccumulator()

        _id = ret.put(Identifier.parse(parser))
        ret.put(parser.consume(TokenType.Assignment))
        expr = ret.put(Expression.parse(parser))

        return ret.map(lambda _: cls(_id.unwrap(), expr.unwrap()))


@dataclass(frozen=True)
class TypeAliasDefine(CommonDirective, HasUniqueID):
    """Узел определение псевдонима типа"""

    type: TypeNode

    @classmethod
    def getIdentifier(cls) -> str:
        return "type"

    @classmethod
    def parse(cls, parser: Parser) -> LogResult[Directive]:
        ret = ResultAccumulator()

        _id = ret.put(Identifier.parse(parser))
        ret.put(parser.consume(TokenType.Assignment))
        _type = ret.put(TypeNode.parse(parser))

        return ret.map(lambda _: cls(_id.unwrap(), _type.unwrap()))

    def accept(self, context: SuperSemanticContext) -> LogResult[None]:
        ret = ResultAccumulator()

        s = self.checkIdentifier(context.getTypes())

        if s is not None:
            ret.put(ErrOne(s))

        profile = ret.put(self.type.accept(context))

        return ret.map(lambda _: context.getTypes().register(self.identifier.id, profile.unwrap()))


@dataclass(frozen=True)
class StructDefine(CommonDirective, HasUniqueID, HasUniqueArguments[Field]):
    """Узел определения структурного типа"""

    @classmethod
    def getIdentifier(cls) -> str:
        return "struct"

    @classmethod
    def parse(cls, parser: Parser) -> LogResult[Directive]:
        ret = ResultAccumulator()

        _id = ret.put(Identifier.parse(parser))
        fields = ret.put(parser.braceArguments(lambda: Field.parse(parser), TokenType.OpenFigure, TokenType.CloseFigure))

        return ret.map(lambda _: cls(fields.unwrap(), _id.unwrap()))

    def accept(self, context: SuperSemanticContext) -> LogResult[None]:
        ret2 = ResultAccumulator()

        s = self.checkIdentifier(context.getTypes())

        if s is not None:
            ret2.put(ErrOne(s))

        if ret2.isErr():
            return ret2.map(lambda _: None)

        ret = ResultAccumulator()

        for field in self.arguments:
            ret.put(field.accept(context))

        return ret.map(lambda _: context.getTypes().register(self.identifier.id, StructTypeProfile(dict(ret.unwrap()))))


@dataclass(frozen=True)
class MacroDefine(CommonDirective, HasUniqueID, HasUniqueArguments[Identifier]):
    """Узел определения макроса"""

    template: Expression
    """Выражение, в которое развертывается макрос"""

    @classmethod
    def getIdentifier(cls) -> str:
        return "macro"

    @classmethod
    def parse(cls, parser: Parser) -> LogResult[Directive]:
        ret = ResultAccumulator()

        _id = ret.put(Identifier.parse(parser))
        args = ret.put(parser.braceArguments(lambda: Identifier.parse(parser), TokenType.OpenRound, TokenType.CloseRound))
        ret.put(parser.consume(TokenType.Arrow))
        expr = ret.put(Expression.parse(parser))

        return ret.map(lambda _: cls(args.unwrap(), _id.unwrap(), expr.unwrap()))

    def accept(self, context: SuperSemanticContext) -> LogResult[None]:
        ret = ResultAccumulator()
        ret.put(self.checkArguments())
        return ret.map(lambda _: context.getMacros().register(self.identifier.id, MacroProfileImpl(tuple(self.arguments), self.template)))
