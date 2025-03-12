from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Sequence

from bytelang.abc.node import Node
from bytelang.abc.semantic import SemanticContext
from bytelang.core.LEGACY_result import LEGACYResultAccumulator
from bytelang.core.LEGACY_result import SingleLEGACYResult
from bytelang.core.ops import Operator
from bytelang.core.result import LogResult


@dataclass(frozen=True)
class MacroProfile[Arg: Node](ABC):
    """Профиль макроса"""

    @abstractmethod
    def expand(self, arguments: Sequence[Arg]) -> LogResult[Arg]:
        """Развернуть макрос"""


class RValueProfile[T](ABC):
    """Профиль правостороннего значения"""

    @classmethod
    @abstractmethod
    def new[T](cls, value: T) -> RValueProfile[T]:
        """Создать профиль правостороннего значения"""

    @abstractmethod
    def getValue(self) -> T:
        """Получить значение профиля"""

    @abstractmethod
    def applyUnaryOperator(self, op: Operator) -> LogResult[RValueProfile[T]]:
        """Применить данный оператор над значением"""

    @abstractmethod
    def applyBinaryOperator(self, other: RValueProfile[T], op: Operator) -> LogResult[RValueProfile[T]]:
        """Применить данный бинарный оператор к значению"""


class TypeProfile[S: SemanticContext](ABC):
    """Профиль типа"""

    @abstractmethod
    def apply[T](self, rvalue: RValueProfile[T], context: S) -> LogResult[bytes]:
        """Применить профиль типа на rvalue"""


@dataclass(frozen=True)
class PackageInstructionProfile:
    """Профиль инструкции пакета"""

    _arguments: Sequence[tuple[str, TypeProfile]]
    """Аргументы инструкции"""

    def packArguments(self, arguments: Sequence[RValueProfile], context: SemanticContext) -> LogResult[bytes]:
        """Упаковка аргументов для вызова инструкции"""

        if (got := len(arguments)) != (need := len(self._arguments)):
            return SingleLEGACYResult.error((f"Invalid arg count: {got} {need=}",))

        ret = LEGACYResultAccumulator()

        for (arg_id, arg_type_profile), arg_value in zip(self._arguments, arguments):
            ret.putMulti(arg_type_profile.apply(arg_value, context).map(err=lambda errors: map(
                lambda e: f"arg {arg_id}: {arg_type_profile} fail pass value {arg_value} : {e}", errors)))

        return ret.map(lambda packed_args: b"".join(packed_args))


@dataclass(frozen=True)
class EnvironmentInstructionProfile[S: SemanticContext]:
    """Профиль инструкции окружения"""

    _package_instruction: PackageInstructionProfile
    """Основание инструкции - инструкция пакета"""
    _code: bytes
    """код инструкции в таблице"""

    def pack(self, arguments: Sequence[RValueProfile], context: S) -> LogResult[bytes]:
        """Упаковка вызова инструкции"""
        return self._package_instruction.packArguments(arguments, context).map(lambda packed_arguments: self._code + packed_arguments)
