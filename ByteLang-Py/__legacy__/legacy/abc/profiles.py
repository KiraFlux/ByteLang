from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Sequence

from bytelang.legacy.abc.node import Node
from bytelang.legacy.abc.semantic import SemanticContext
from bytelang.core.ops import Operator
from bytelang.legacy.core.result import LogResult


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
    def pack[T](self, rvalue: RValueProfile[T], context: S) -> LogResult[bytes]:
        """Применить профиль типа на rvalue"""

    @abstractmethod
    def getSize(self, context: S) -> int:
        """Получить размер типа профиля в байтах"""


@dataclass(frozen=True)
class VariableProfile[S: SemanticContext, T]:
    """Профиль значения"""

    _type: TypeProfile[S]
    """Профиль типа"""
    _value: RValueProfile[T]
    """Профиль значения инициализации"""
    address: RValueProfile[int]
    """Адрес значения"""

    def pack(self, context: S) -> LogResult[bytes]:
        """Упаковка значения"""
        return self._type.pack(self._value, context)

    def getSize(self, context: S) -> int:
        """Получить размер значения"""
        return self._type.getSize(context)


@dataclass(frozen=True)
class PackageInstructionProfile:
    """Профиль инструкции пакета"""

    _arguments: Sequence[tuple[str, TypeProfile]]
    """Аргументы инструкции"""

    def packArguments(self, arguments: Sequence[RValueProfile], context: SemanticContext) -> LogResult[NotImplemented]:
        """Упаковка аргументов для вызова инструкции"""
        raise NotImplementedError


@dataclass(frozen=True)
class EnvironmentInstructionProfile[S: SemanticContext]:
    """Профиль инструкции окружения"""

    _package_instruction: PackageInstructionProfile
    """Основание инструкции - инструкция пакета"""
    _code: bytes
    """код инструкции в таблице"""

    def pack(self, arguments: Sequence[RValueProfile], context: S) -> LogResult[NotImplemented]:
        """Упаковка вызова инструкции"""
        raise NotImplementedError
