from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable

from bytelang.abc.parser import Parser
from bytelang.core.result import MultiErrorResult
from bytelang.core.result import Result
from bytelang.core.result import SingleResult
from bytelang.impl.node.directive.super import Directive
from bytelang.impl.node.expression import HasExistingID
from bytelang.impl.node.expression import HasUniqueID
from bytelang.impl.node.expression import Identifier
from bytelang.impl.semantizer.sketch import SketchSemanticContext


class SourceDirective(Directive[SketchSemanticContext], ABC):
    """Директива, исполняемая в скетче"""

    @abstractmethod
    def accept(self, context: SketchSemanticContext) -> Result[None, Iterable[str]]:
        pass


@dataclass(frozen=True)
class SelectEnvironment(SourceDirective, HasExistingID):
    """Директива выбора окружения"""

    @classmethod
    def getIdentifier(cls) -> str:
        return "env"

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        return Identifier.parse(parser).map(lambda ok: cls(ok))

    def accept(self, context: SketchSemanticContext) -> Result[None, Iterable[str]]:
        ret = MultiErrorResult()

        if context.selected_environment is not None:
            ret.putOptionalError(f"Env already selected: {context.selected_environment}")

        env = ret.putSingle(context.environment_registry.get(self.identifier.id))

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

    def accept(self, context: SketchSemanticContext) -> Result[None, Iterable[str]]:
        err = self.checkIdentifier(NotImplemented)

        if err is None:
            return SingleResult.error(err)

        return SingleResult.ok(None)
