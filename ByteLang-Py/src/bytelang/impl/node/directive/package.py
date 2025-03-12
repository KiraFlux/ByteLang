"""Реализации директив для файлов пакета"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass

from bytelang.abc.parser import Parser
from bytelang.abc.profiles import PackageInstructionProfile
from bytelang.core.result import ErrOne
from bytelang.core.result import LogResult
from bytelang.core.result import ResultAccumulator
from bytelang.core.tokens import TokenType
from bytelang.impl.node.component import HasUniqueArguments
from bytelang.impl.node.directive.super import Directive
from bytelang.impl.node.expression import HasUniqueID
from bytelang.impl.node.expression import Identifier
from bytelang.impl.node.type import Field
from bytelang.impl.semantizer.package import PackageSemanticContext


class PackageDirective(Directive[PackageSemanticContext], ABC):
    """Директива, исполняемая в пакетах"""

    @abstractmethod
    def accept(self, context: PackageSemanticContext) -> LogResult[None]:
        pass


@dataclass(frozen=True)
class InstructionDefine(PackageDirective, HasUniqueID, HasUniqueArguments[Field]):
    """Узел определения структуры"""

    @classmethod
    def getIdentifier(cls) -> str:
        return "inst"

    @classmethod
    def parse(cls, parser: Parser) -> LogResult[Directive]:
        ret = ResultAccumulator()

        _id = ret.put(Identifier.parse(parser))
        args = ret.put(parser.braceArguments(lambda: Field.parse(parser), TokenType.OpenRound, TokenType.CloseRound))

        return ret.map(lambda _: cls(args.unwrap(), _id.unwrap()))

    def accept(self, context: PackageSemanticContext) -> LogResult[None]:
        ret_0 = ResultAccumulator()

        s = self.checkIdentifier(context.instruction_registry)

        if s is not None:
            ret_0.put(ErrOne(s))

        if ret_0.isErr():
            return ret_0.map(lambda _: None)

        ret_1 = ResultAccumulator()

        for arg in self.arguments:
            ret_1.put(arg.accept(context))

        return ret_1.map(lambda fields: context.instruction_registry.register(self.identifier.id, PackageInstructionProfile(fields)))
