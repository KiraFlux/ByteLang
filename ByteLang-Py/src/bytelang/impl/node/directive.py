from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable
from typing import Optional

from bytelang.abc.parser import Parser
from bytelang.abc.profiles import PackageInstructionProfile
from bytelang.abc.semantic import SemanticContext
from bytelang.core.result import MultiErrorResult
from bytelang.core.result import Result
from bytelang.core.result import ResultAccumulator
from bytelang.core.result import SingleResult
from bytelang.core.tokens import TokenType
from bytelang.impl.node.component import HasUniqueArguments
from bytelang.impl.node.expression import Expression
from bytelang.impl.node.expression import HasExistingID
from bytelang.impl.node.expression import HasUniqueID
from bytelang.impl.node.expression import Identifier
from bytelang.impl.node.statement import Statement
from bytelang.impl.node.type import Field
from bytelang.impl.node.type import TypeNode
from bytelang.impl.profiles.macro import MacroProfileImpl
from bytelang.impl.profiles.type import StructTypeProfile
from bytelang.impl.semantizer.common import CommonSemanticContext
from bytelang.impl.semantizer.env import EnvironmentSemanticContext
from bytelang.impl.semantizer.package import PackageSemanticContext
from bytelang.impl.semantizer.source import SourceSemanticContext


class Directive[S: SemanticContext](Statement[S], ABC):
    """Узел Директивы"""

    @classmethod
    @abstractmethod
    def getIdentifier(cls) -> str:
        """Получить идентификатор директивы"""


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


class EnvironmentDirective(Directive[EnvironmentSemanticContext], ABC):
    """Директива, исполняемая в файлах конфигурации окружения"""

    @abstractmethod
    def accept(self, context: EnvironmentSemanticContext) -> Result[None, Iterable[str]]:
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

    @classmethod
    def getIdentifier(cls) -> str:
        return "const"

    def accept(self, context: CommonSemanticContext) -> Result[None, Iterable[str]]:
        ret = MultiErrorResult()

        ret.putOptionalError(self.checkIdentifier(context.const_registry))
        expr_value = ret.putMulti(self.expression.accept(context))

        if ret.isOk():
            context.const_registry.register(self.identifier.id, expr_value.unwrap())

        return ret.make(lambda: None)

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        ret = MultiErrorResult()

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
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        ret = MultiErrorResult()

        _id = ret.putMulti(Identifier.parse(parser))
        ret.putSingle(parser.consume(TokenType.Assignment))
        _type = ret.putMulti(TypeNode.parse(parser))

        return ret.make(lambda: cls(_id.unwrap(), _type.unwrap()))

    def accept(self, context: CommonSemanticContext) -> Result[None, Iterable[str]]:
        ret = MultiErrorResult()

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
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        ret = MultiErrorResult()

        _id = ret.putSingle(Identifier.parse(parser))
        fields = ret.putMulti(parser.braceArguments(lambda: Field.parse(parser), TokenType.OpenFigure, TokenType.CloseFigure))

        return ret.make(lambda: cls(fields.unwrap(), _id.unwrap()))

    def accept(self, context: CommonSemanticContext) -> Result[None, Iterable[str]]:
        ret2 = MultiErrorResult()

        ret2.putOptionalError(self.checkIdentifier(context.type_registry))
        ret2.putMulti(self.checkArguments())

        if ret2.isError():
            return ret2.make(lambda: None)

        ret = ResultAccumulator()

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
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        ret = MultiErrorResult()

        _id = ret.putSingle(Identifier.parse(parser))
        args = ret.putMulti(parser.braceArguments(lambda: Identifier.parse(parser), TokenType.OpenRound, TokenType.CloseRound))
        ret.putSingle(parser.consume(TokenType.Arrow))
        expr = ret.putMulti(Expression.parse(parser))

        return ret.make(lambda: cls(args.unwrap(), _id.unwrap(), expr.unwrap()))

    def accept(self, context: CommonSemanticContext) -> Result[None, Iterable[str]]:
        ret = MultiErrorResult()

        ret.putMulti(self.checkArguments())

        return ret.make(lambda: context.macro_registry.register(self.identifier.id, MacroProfileImpl(tuple(self.arguments), self.template)))


@dataclass(frozen=True)
class InstructionDefine(PackageDirective, HasUniqueID, HasUniqueArguments[Field]):
    """Узел определения структуры"""

    @classmethod
    def getIdentifier(cls) -> str:
        return "inst"

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        ret = MultiErrorResult()

        _id = ret.putSingle(Identifier.parse(parser))
        args = ret.putMulti(parser.braceArguments(lambda: Field.parse(parser), TokenType.OpenRound, TokenType.CloseRound))

        return ret.make(lambda: cls(args.unwrap(), _id.unwrap()))

    def accept(self, context: PackageSemanticContext) -> Result[None, Iterable[str]]:
        ret_0 = MultiErrorResult()
        ret_0.putOptionalError(self.checkIdentifier(context.instruction_registry))
        ret_0.putMulti(self.checkArguments())

        if ret_0.isError():
            return ret_0.make(lambda: None)

        ret_1 = ResultAccumulator()

        for arg in self.arguments:
            ret_1.putMulti(arg.accept(context))

        return ret_1.map(lambda fields: context.instruction_registry.register(self.identifier.id, PackageInstructionProfile(fields)))


@dataclass(frozen=True)
class UsePackage(EnvironmentDirective, HasExistingID):
    """Выбрать пакет инструкций"""

    selected_instructions: Optional[Iterable[Identifier]]

    """
    Выбранные инструкции для использования
    None - используются все инструкции
    
    .use package
    .use package{inst_1, inst_2}  
    """

    @classmethod
    def getIdentifier(cls) -> str:
        return "use"

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        ret = MultiErrorResult()

        _package = ret.putMulti(Identifier.parse(parser))
        _instructions = ret.putMulti(cls._parseUsedInstructions(parser))

        return ret.make(lambda: cls(_package.unwrap(), _instructions.unwrap()))

    def accept(self, context: EnvironmentSemanticContext) -> Result[None, Iterable[str]]:
        # пакет ещё не был загружен
        # что пакет существует
        # что выбранные инструкции существуют
        pass

    @classmethod
    def _parseUsedInstructions(cls, parser: Parser) -> Result[Optional[Iterable[Identifier]], Iterable[str]]:
        if parser.tokens.peek().type == TokenType.OpenFigure:
            return parser.braceArguments(lambda: Identifier.parse(parser), TokenType.OpenFigure, TokenType.CloseFigure)

        return SingleResult.ok(None)


@dataclass(frozen=True)
class EnvSelect(SourceDirective, HasExistingID):
    """Директива выбора окружения"""

    @classmethod
    def getIdentifier(cls) -> str:
        return "env"

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        return Identifier.parse(parser).map(lambda ok: cls(ok))

    def accept(self, context: SourceSemanticContext) -> Result[None, Iterable[str]]:
        ret = MultiErrorResult()

        if context.selected_environment is not None:
            ret.putOptionalError(f"Env already selected: {context.selected_environment}")

        env = ret.putSingle(self.checkIdentifier(context.environment_registry))

        if ret.isOk():
            context.selected_environment = env.unwrap()

        return ret.make(lambda: None)


@dataclass(frozen=True)
class MarkDefine(SourceDirective, HasUniqueID):
    """Узел определения метки"""

    @classmethod
    def getIdentifier(cls) -> str:
        return "mark"

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        return Identifier.parse(parser).map(lambda ok: cls(ok))

    def accept(self, context: SourceSemanticContext) -> Result[None, Iterable[str]]:
        err = self.checkIdentifier(NotImplemented)

        if err is None:
            return SingleResult.error(err)

        return SingleResult.ok(None)
