"""Директивы для файлов настройки окружения"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable
from typing import Iterable
from typing import Mapping
from typing import Optional

from bytelang.abc.parser import Parser
from bytelang.abc.profiles import EnvironmentInstructionProfile
from bytelang.abc.profiles import PackageInstructionProfile
from bytelang.abc.registry import Registry
from bytelang.abc.serializer import Serializer
from bytelang.core.LEGACY_result import MultiErrorLEGACYResult
from bytelang.core.LEGACY_result import LEGACY_Result
from bytelang.core.LEGACY_result import LEGACYResultAccumulator
from bytelang.core.LEGACY_result import SingleLEGACYResult
from bytelang.core.tokens import TokenType
from bytelang.impl.node.directive.super import Directive
from bytelang.impl.node.expression import HasExistingID
from bytelang.impl.node.expression import Identifier
from bytelang.impl.semantizer.env import EnvironmentSemanticContext


class EnvironmentDirective(Directive[EnvironmentSemanticContext], ABC):
    """Директива, исполняемая в файлах конфигурации окружения"""

    @abstractmethod
    def accept(self, context: EnvironmentSemanticContext) -> LEGACY_Result[None, Iterable[str]]:
        pass


class _SetEnvSpecialPointer(EnvironmentDirective, HasExistingID, ABC):
    """Установить примитивный тип для ширины указателя инструкции"""

    _ptr_type_suffix: str

    @classmethod
    def getIdentifier(cls) -> str:
        return f"ptr_{cls._ptr_type_suffix}"

    @staticmethod
    @abstractmethod
    def _getSetter(context: EnvironmentSemanticContext) -> Callable[[Serializer[int]], None]:
        """Получить установщик указателя"""

    @classmethod
    def parse(cls, parser: Parser) -> LEGACY_Result[_SetEnvSpecialPointer, Iterable[str]]:
        return Identifier.parse(parser).map(lambda _id: cls(_id))

    def accept(self, context: EnvironmentSemanticContext) -> LEGACY_Result[None, Iterable[str]]:
        return context.primitive_serializers_registry.get(self.identifier.id).map(lambda s: self._getSetter(context)(s), lambda e: (e,))


class SetEnvInstructionPointer(_SetEnvSpecialPointer):
    _ptr_type_suffix = "inst"

    @staticmethod
    def _getSetter(context: EnvironmentSemanticContext) -> Callable[[Serializer[int]], None]:
        def _s(s):
            context.instruction_pointer = s

        return _s


class SetEnvProgramPointer(_SetEnvSpecialPointer):
    _ptr_type_suffix = "prog"

    @staticmethod
    def _getSetter(context: EnvironmentSemanticContext) -> Callable[[Serializer[int]], None]:
        def _s(s):
            context.program_pointer = s

        return _s


class SetEnvDataPointer(_SetEnvSpecialPointer):
    _ptr_type_suffix = "data"

    @staticmethod
    def _getSetter(context: EnvironmentSemanticContext) -> Callable[[Serializer[int]], None]:
        def _s(s):
            context.data_pointer = s

        return _s


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
    def parse(cls, parser: Parser) -> LEGACY_Result[Directive, Iterable[str]]:
        ret = MultiErrorLEGACYResult()

        _package = ret.putMulti(Identifier.parse(parser))
        _instructions = ret.putMulti(cls._parseUsedInstructions(parser))

        return ret.make(lambda: cls(_package.unwrap(), _instructions.unwrap()))

    def accept(self, context: EnvironmentSemanticContext) -> LEGACY_Result[None, Iterable[str]]:
        # что пакет существует
        package_result = context.package_registry.get(self.identifier.id)

        if package_result.isError():
            return package_result.map(err=lambda e: (e,))

        # что выбранные инструкции существуют
        chosen_result = self._acceptChosenInstructions(package_result.unwrap().instructions)

        if chosen_result.isError():
            return chosen_result.flow()

        env_result = self._acceptEnvInstructions(chosen_result.unwrap(), context)

        if env_result.isError():
            return env_result.flow()

        ret = MultiErrorLEGACYResult()

        for env_inst_key, env_inst_value in env_result.unwrap().items():
            if context.instruction_registry.has(env_inst_key):
                ret.putOptionalError(f"{env_inst_key} already exist in {context}")
            else:
                context.instruction_registry.register(env_inst_key, env_inst_value)

        return ret.make(lambda: None)

    @staticmethod
    def _acceptEnvInstructions(
            package_instructions: Mapping[str, PackageInstructionProfile],
            context: EnvironmentSemanticContext
    ) -> LEGACY_Result[Mapping[str, EnvironmentInstructionProfile], Iterable[str]]:

        if context.instruction_pointer is None:
            return SingleLEGACYResult.error((f"{context.instruction_pointer=}",))

        ret = LEGACYResultAccumulator()
        package_instruction_index_offset: int = len(context.instruction_registry.getMappingView())

        for offset, (inst_key, package_inst) in enumerate(package_instructions.items()):
            ret.putMulti(
                context.instruction_pointer.pack(package_instruction_index_offset + offset)
                .map(lambda code: (inst_key, EnvironmentInstructionProfile(package_inst, code)))
            )

        return ret.map(lambda items: dict(items))

    def _acceptChosenInstructions(self, instructions: Registry[str, PackageInstructionProfile, str]) -> LEGACY_Result[Mapping[str, PackageInstructionProfile], Iterable[str]]:
        if self.selected_instructions is None:
            return SingleLEGACYResult.ok(instructions.getMappingView())

        ret = LEGACYResultAccumulator()

        for selected in self.selected_instructions:
            ret.putSingle(instructions.get(selected.id).map(lambda ins: (selected.id, ins)))

        return ret.map(lambda items: dict(items))

    @classmethod
    def _parseUsedInstructions(cls, parser: Parser) -> LEGACY_Result[Optional[Iterable[Identifier]], Iterable[str]]:
        if parser.tokens.peek().type == TokenType.OpenFigure:
            return parser.braceArguments(lambda: Identifier.parse(parser), TokenType.OpenFigure, TokenType.CloseFigure)

        return SingleLEGACYResult.ok(None)
