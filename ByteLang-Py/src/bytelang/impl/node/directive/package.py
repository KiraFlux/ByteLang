"""Реализации директив для файлов пакета"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable

from bytelang.abc.parser import Parser
from bytelang.abc.profiles import PackageInstructionProfile
from bytelang.core.LEGACY_result import MultiErrorLEGACYResult
from bytelang.core.LEGACY_result import LEGACY_Result
from bytelang.core.LEGACY_result import LEGACYResultAccumulator
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
    def accept(self, context: PackageSemanticContext) -> LEGACY_Result[None, Iterable[str]]:
        pass


@dataclass(frozen=True)
class InstructionDefine(PackageDirective, HasUniqueID, HasUniqueArguments[Field]):
    """Узел определения структуры"""

    @classmethod
    def getIdentifier(cls) -> str:
        return "inst"

    @classmethod
    def parse(cls, parser: Parser) -> LEGACY_Result[Directive, Iterable[str]]:
        ret = MultiErrorLEGACYResult()

        _id = ret.putSingle(Identifier.parse(parser))
        args = ret.putMulti(parser.braceArguments(lambda: Field.parse(parser), TokenType.OpenRound, TokenType.CloseRound))

        return ret.make(lambda: cls(args.unwrap(), _id.unwrap()))

    def accept(self, context: PackageSemanticContext) -> LEGACY_Result[None, Iterable[str]]:
        ret_0 = MultiErrorLEGACYResult()
        ret_0.putOptionalError(self.checkIdentifier(context.instruction_registry))
        ret_0.putMulti(self.checkArguments())

        if ret_0.isError():
            return ret_0.make(lambda: None)

        ret_1 = LEGACYResultAccumulator()

        for arg in self.arguments:
            ret_1.putMulti(arg.accept(context))

        return ret_1.map(lambda fields: context.instruction_registry.register(self.identifier.id, PackageInstructionProfile(fields)))
