from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass

from bytelang.legacy.abc.parser import Parser
from bytelang.legacy.core.result import ErrOne
from bytelang.legacy.core.result import LogResult
from bytelang.legacy.core.result import ResultAccumulator
from bytelang.legacy.core.tokens import TokenType
from bytelang.legacy.impl.node.directive.super import Directive
from bytelang.legacy.impl.node.expression import Expression
from bytelang.legacy.impl.node.expression import HasExistingID
from bytelang.legacy.impl.node.expression import HasUniqueID
from bytelang.legacy.impl.node.expression import Identifier
from bytelang.legacy.impl.node.type import Field
from bytelang.legacy.impl.semantizer.sketch import SketchSemanticContext


class SketchDirective(Directive[SketchSemanticContext], ABC):
    """Директива, исполняемая в скетче"""

    @abstractmethod
    def accept(self, context: SketchSemanticContext) -> LogResult[None]:
        pass


@dataclass(frozen=True)
class SelectEnvironment(SketchDirective, HasExistingID):
    """Директива выбора окружения"""

    @classmethod
    def getIdentifier(cls) -> str:
        return "env"

    @classmethod
    def parse(cls, parser: Parser) -> LogResult[Directive]:
        return Identifier.parse(parser).map(lambda ok: cls(ok))

    def accept(self, context: SketchSemanticContext) -> LogResult[None]:
        ret = ResultAccumulator()

        if context.selected_environment is not None:
            ret.put(ErrOne(f"Env already selected: {context.selected_environment}"))

        get = context.environment_registry.get(self.identifier.id)
        env = ret.put(get)

        if ret.isOk():
            context.selected_environment = env.unwrap()

        return ret.map(lambda _: None)


@dataclass(frozen=True)
class VarDefine(SketchDirective):
    """Узел определения значения"""

    field: Field
    """Поле значения"""
    initializer: Expression
    """Выражение инициализации"""

    def accept(self, context: SketchSemanticContext) -> LogResult[None]:
        var_id = self.field.identifier.id

        if context._var_registry.has(var_id):
            return ErrOne(f"Name already defined: {self}")

        ret = ResultAccumulator()

        _type = ret.put(self.field.type.accept(context))
        _init = ret.put(self.initializer.accept(context))

        return ret.map().andThen(context.addVar(var_id, _type.unwrap(), _init.unwrap()))

    @classmethod
    def parse(cls, parser: Parser) -> LogResult[VarDefine]:
        """.var a: u16 = 12345"""
        ret = ResultAccumulator()

        field = ret.put(Field.parse(parser))
        ret.put(parser.consume(TokenType.Assignment))
        initializer = ret.put(Expression.parse(parser))

        return ret.map(lambda _: cls(field.unwrap(), initializer.unwrap()))

    @classmethod
    def getIdentifier(cls) -> str:
        return "var"


@dataclass(frozen=True)
class MarkDefine(SketchDirective, HasUniqueID):
    """Узел определения метки"""

    @classmethod
    def getIdentifier(cls) -> str:
        return "mark"

    @classmethod
    def parse(cls, parser: Parser) -> LogResult[Directive]:
        return Identifier.parse(parser).map(lambda ok: cls(ok))

    def accept(self, context: SketchSemanticContext) -> LogResult[None]:
        raise NotImplementedError
        # err = self.checkIdentifier(NotImplemented)
        #
        # if err is not None:
        #     return ErrOne(err)
        #
        # return Ok(lambda: context.mark_registry.register(self.identifier.id, IntegerRV.new(len(context.instructions_code))))
