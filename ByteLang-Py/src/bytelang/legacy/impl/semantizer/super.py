"""Абстрактный общий контекст"""
from abc import ABC
from abc import abstractmethod

from bytelang.legacy.abc.profiles import MacroProfile
from bytelang.legacy.abc.profiles import RValueProfile
from bytelang.legacy.abc.profiles import TypeProfile
from bytelang.legacy.abc.registry import MutableRegistry
from bytelang.legacy.abc.semantic import SemanticContext


class SuperSemanticContext[T](SemanticContext[T], ABC):
    """Абстрактный общий контекст семантического анализа"""

    @abstractmethod
    def getConstants(self) -> MutableRegistry[str, RValueProfile]:
        """Получить изменяемый реестр констант"""

    @abstractmethod
    def getMacros(self) -> MutableRegistry[str, MacroProfile]:
        """Получить изменяемый реестр макросов"""

    @abstractmethod
    def getTypes(self) -> MutableRegistry[str, TypeProfile]:
        """Получить изменяемый реестр типов"""
