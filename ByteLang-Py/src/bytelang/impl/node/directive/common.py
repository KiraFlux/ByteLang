"""Реализации директив общего назначения"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable

from bytelang.abc.parser import Parser
from bytelang.core.LEGACY_result import MultiErrorLEGACYResult
from bytelang.core.LEGACY_result import LEGACY_Result
from bytelang.core.LEGACY_result import LEGACYResultAccumulator
from bytelang.core.tokens import TokenType
from bytelang.impl.node.component import HasUniqueArguments
from bytelang.impl.node.directive.super import Directive
from bytelang.impl.node.expression import Expression
from bytelang.impl.node.expression import HasUniqueID
from bytelang.impl.node.expression import Identifier
from bytelang.impl.node.type import Field
from bytelang.impl.node.type import TypeNode
from bytelang.impl.profiles.macro import MacroProfileImpl
from bytelang.impl.profiles.type import StructTypeProfile
from bytelang.impl.semantizer.common import CommonSemanticContext


class CommonDirective(Directive[CommonSemanticContext], ABC):
    """Директива общего назначения"""

    @abstractmethod
    def accept(self, context: CommonSemanticContext) -> LEGACY_Result[None, Iterable[str]]:
        pass


@dataclass(frozen=True)
class ConstDefine(CommonDirective, HasUniqueID):
    """Узел определения константного значения"""

    expression: Expression
    """Выражение значения"""

    @classmethod
    def getIdentifier(cls) -> str:
        return "const"

    def accept(self, context: CommonSemanticContext) -> LEGACY_Result[None, Iterable[str]]:
        ret = MultiErrorLEGACYResult()

        ret.putOptionalError(self.checkIdentifier(context.const_registry))
        expr_value = ret.putMulti(self.expression.accept(context))

        return ret.make(lambda: context.const_registry.register(self.identifier.id, expr_value.unwrap()))

    @classmethod
    def parse(cls, parser: Parser) -> LEGACY_Result[Directive, Iterable[str]]:
        ret = MultiErrorLEGACYResult()

        _id = ret.putSingle(Identifier.parse(parser))
        ret.putSingle(parser.consume(TokenType.Assignment))
        expr = ret.putMulti(Expression.parse(parser))

        return ret.make(lambda: cls(_id.unwrap(), expr.unwrap()))


@dataclass(frozen=True)
class TypeAliasDefine(CommonDirective, HasUniqueID):
    """Узел определение псевдонима типа"""

    type: TypeNode

    @classmethod
    def getIdentifier(cls) -> str:
        return "type"

    @classmethod
    def parse(cls, parser: Parser) -> LEGACY_Result[Directive, Iterable[str]]:
        ret = MultiErrorLEGACYResult()

        _id = ret.putMulti(Identifier.parse(parser))
        ret.putSingle(parser.consume(TokenType.Assignment))
        _type = ret.putMulti(TypeNode.parse(parser))

        return ret.make(lambda: cls(_id.unwrap(), _type.unwrap()))

    def accept(self, context: CommonSemanticContext) -> LEGACY_Result[None, Iterable[str]]:
        ret = MultiErrorLEGACYResult()

        ret.putOptionalError(self.checkIdentifier(context.type_registry))
        profile = ret.putMulti(self.type.accept(context))

        return ret.make(lambda: context.type_registry.register(self.identifier.id, profile.unwrap()))


@dataclass(frozen=True)
class StructDefine(CommonDirective, HasUniqueID, HasUniqueArguments[Field]):
    """Узел определения структурного типа"""

    @classmethod
    def getIdentifier(cls) -> str:
        return "struct"

    @classmethod
    def parse(cls, parser: Parser) -> LEGACY_Result[Directive, Iterable[str]]:
        ret = MultiErrorLEGACYResult()

        _id = ret.putSingle(Identifier.parse(parser))
        fields = ret.putMulti(parser.braceArguments(lambda: Field.parse(parser), TokenType.OpenFigure, TokenType.CloseFigure))

        return ret.make(lambda: cls(fields.unwrap(), _id.unwrap()))

    def accept(self, context: CommonSemanticContext) -> LEGACY_Result[None, Iterable[str]]:
        ret2 = MultiErrorLEGACYResult()

        ret2.putOptionalError(self.checkIdentifier(context.type_registry))
        ret2.putMulti(self.checkArguments())

        if ret2.isError():
            return ret2.make(lambda: None)

        ret = LEGACYResultAccumulator()

        for field in self.arguments:
            ret.putMulti(field.accept(context))

        return ret.map(lambda _: context.type_registry.register(self.identifier.id, StructTypeProfile(dict(ret.unwrap()))))


@dataclass(frozen=True)
class MacroDefine(CommonDirective, HasUniqueID, HasUniqueArguments[Identifier]):
    """Узел определения макроса"""

    template: Expression
    """Выражение, в которое развертывается макрос"""

    @classmethod
    def getIdentifier(cls) -> str:
        return "macro"

    @classmethod
    def parse(cls, parser: Parser) -> LEGACY_Result[Directive, Iterable[str]]:
        ret = MultiErrorLEGACYResult()

        _id = ret.putSingle(Identifier.parse(parser))
        args = ret.putMulti(parser.braceArguments(lambda: Identifier.parse(parser), TokenType.OpenRound, TokenType.CloseRound))
        ret.putSingle(parser.consume(TokenType.Arrow))
        expr = ret.putMulti(Expression.parse(parser))

        return ret.make(lambda: cls(args.unwrap(), _id.unwrap(), expr.unwrap()))

    def accept(self, context: CommonSemanticContext) -> LEGACY_Result[None, Iterable[str]]:
        ret = MultiErrorLEGACYResult()

        ret.putMulti(self.checkArguments())

        return ret.make(lambda: context.macro_registry.register(self.identifier.id, MacroProfileImpl(tuple(self.arguments), self.template)))
