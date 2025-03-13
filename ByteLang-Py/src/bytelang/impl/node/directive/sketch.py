from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass

from bytelang.abc.parser import Parser
from bytelang.core.result import ErrOne
from bytelang.core.result import LogResult
from bytelang.core.result import Ok
from bytelang.core.result import ResultAccumulator
from bytelang.impl.node.directive.super import Directive
from bytelang.impl.node.expression import HasExistingID
from bytelang.impl.node.expression import HasUniqueID
from bytelang.impl.node.expression import Identifier
from bytelang.impl.profiles.rvalue import IntegerRV
from bytelang.impl.semantizer.sketch import SketchSemanticContext


class SourceDirective(Directive[SketchSemanticContext], ABC):
    """Директива, исполняемая в скетче"""

    @abstractmethod
    def accept(self, context: SketchSemanticContext) -> LogResult[None]:
        pass


@dataclass(frozen=True)
class SelectEnvironment(SourceDirective, HasExistingID):
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
class MarkDefine(SourceDirective, HasUniqueID):
    """Узел определения метки"""

    @classmethod
    def getIdentifier(cls) -> str:
        return "mark"

    @classmethod
    def parse(cls, parser: Parser) -> LogResult[Directive]:
        return Identifier.parse(parser).map(lambda ok: cls(ok))

    def accept(self, context: SketchSemanticContext) -> LogResult[None]:
        err = self.checkIdentifier(NotImplemented)

        if err is not None:
            return ErrOne(err)

        return Ok(lambda: context.mark_registry.register(self.identifier.id, IntegerRV.new(len(context.instructions_code))))
