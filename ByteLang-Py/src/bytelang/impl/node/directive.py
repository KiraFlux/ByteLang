from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable

from bytelang.abc.parser import Parser
from bytelang.abc.semantic import SemanticContext
from bytelang.core.tokens import TokenType
from bytelang.impl.node.expression import Expression
from bytelang.impl.node.expression import Identifier
from bytelang.impl.node.statement import Statement
from bytelang.impl.node.super import HasArguments
from bytelang.impl.node.super import HasExistingID
from bytelang.impl.node.super import HasUniqueID
from bytelang.impl.node.type import Field
from bytelang.impl.semantizer.common import CommonSemanticContext
from bytelang.impl.semantizer.package import PackageSemanticContext
from bytelang.impl.semantizer.source import SourceSemanticContext
from rustpy.result import MultipleErrorsResult
from rustpy.result import Result
from rustpy.result import ResultAccumulator
from rustpy.result import SingleResult


class Directive[S: SemanticContext](Statement[S], ABC):
    """Узел Директивы"""


class CommonDirective(Directive[CommonSemanticContext], ABC):
    """Директива общего назначения"""

    @abstractmethod
    def accept(self, context: CommonSemanticContext) -> Result[None, Iterable[str]]:
        pass


class PackageDirective(Directive[PackageSemanticContext], ABC):
    """Директива, исполняемая в пакетах"""

    @abstractmethod
    def accept(self, context: PackageSemanticContext) -> Result[None, Iterable[str]]:
        pass


class SourceDirective(Directive[SourceSemanticContext], ABC):
    """Директива, исполняемая в исполняемых скриптах"""

    @abstractmethod
    def accept(self, context: SourceSemanticContext) -> Result[None, Iterable[str]]:
        pass


@dataclass(frozen=True)
class ConstDefine(CommonDirective, HasUniqueID):
    """Узел определения константного значения"""

    expression: Expression
    """Выражение значения"""

    def accept(self, context: CommonSemanticContext) -> Result[None, Iterable[str]]:
        ret = MultipleErrorsResult()

        ret.putOptionalError(self.checkIdentifier(context.const_registry))
        expr_value = ret.putMulti(self.expression.accept(context))

        if ret.isOk():
            context.const_registry.register(self.identifier, expr_value.unwrap())

        return ret.make(lambda: None)

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        ret = MultipleErrorsResult()

        _id = ret.putSingle(Identifier.parse(parser))
        ret.putSingle(parser.consume(TokenType.Assignment))
        expr = ret.putMulti(Expression.parse(parser))

        return ret.make(lambda: cls(_id.unwrap(), expr.unwrap()))


@dataclass(frozen=True)
class StructDefine(CommonDirective, HasUniqueID, HasArguments[Field]):
    """Узел определения структурного типа"""

    def accept(self, context: CommonSemanticContext) -> Result[None, Iterable[str]]:
        ret = ResultAccumulator()

        ret.putOptionalError(self.checkIdentifier(context.type_registry))
        ret.putMulti(self.checkArguments(context))

        if ret.isOk():
            fi = ret.unwrap()
            context.type_registry.register(self.identifier, NotImplemented)  # TODO реализовать

        return ret.map(lambda _: None)

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        ret = MultipleErrorsResult()

        _id = ret.putSingle(Identifier.parse(parser))
        fields = ret.putMulti(parser.braceArguments(lambda: Field.parse(parser), TokenType.OpenFigure, TokenType.CloseFigure))

        return ret.make(lambda: cls(fields.unwrap(), _id.unwrap()))


@dataclass(frozen=True)
class MacroDefine(CommonDirective, HasUniqueID, HasArguments[Identifier]):
    """Узел определения макроса"""

    expression: Expression
    """Выражение, в которое развертывается макрос"""

    def accept(self, context: CommonSemanticContext) -> Result[None, Iterable[str]]:
        ret = ResultAccumulator()
        ret.putMulti(self.checkArguments(context))

        if ret.isOk():
            context.macro_registry.register(self.identifier, self)

        return ret.map(lambda _: None)

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        ret = MultipleErrorsResult()

        _id = ret.putSingle(Identifier.parse(parser))
        args = ret.putMulti(parser.braceArguments(lambda: Identifier.parse(parser), TokenType.OpenRound, TokenType.CloseRound))
        ret.putSingle(parser.consume(TokenType.Arrow))
        expr = ret.putMulti(Expression.parse(parser))

        return ret.make(lambda: cls(args.unwrap(), _id.unwrap(), expr.unwrap()))


@dataclass(frozen=True)
class InstructionDefine(PackageDirective, HasUniqueID, HasArguments[Field]):
    """Узел определения структуры"""

    # TODO решить как будет работать Field
    def accept(self, context: PackageSemanticContext) -> Result[None, Iterable[str]]:
        ret = ResultAccumulator()

        ret.putOptionalError(self.checkIdentifier(NotImplemented))
        ret.putMulti(self.checkArguments(context))

        return ret.map(lambda _: None)

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        ret = MultipleErrorsResult()

        _id = ret.putSingle(Identifier.parse(parser))
        args = ret.putMulti(parser.braceArguments(lambda: Field.parse(parser), TokenType.OpenRound, TokenType.CloseRound))

        return ret.make(lambda: cls(args.unwrap(), _id.unwrap()))


@dataclass(frozen=True)
class EnvSelect(SourceDirective, HasExistingID):
    """Директива выбора окружения"""

    def accept(self, context: SourceSemanticContext) -> Result[None, Iterable[str]]:
        ret = MultipleErrorsResult()

        if context.selected_environment is not None:
            ret.putOptionalError(f"Env already selected: {context.selected_environment}")

        env = ret.putSingle(self.checkIdentifier(context.environment_registry))

        if ret.isOk():
            context.selected_environment = env.unwrap()

        return ret.make(lambda: None)

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        return Identifier.parse(parser).map(lambda ok: cls(ok))


@dataclass(frozen=True)
class MarkDefine(SourceDirective, HasUniqueID):
    """Узел определения метки"""

    def accept(self, context: SourceSemanticContext) -> Result[None, Iterable[str]]:
        err = self.checkIdentifier(NotImplemented)

        if err is None:
            return SingleResult.error(err)

        return SingleResult.ok(None)

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        return Identifier.parse(parser).map(lambda ok: cls(ok))
