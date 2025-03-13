"""
Составной контекст семантического анализатора - обёртка над интерфейсом Super ... ,
"""
from abc import ABC
from typing import Final

from bytelang.abc.profiles import MacroProfile
from bytelang.abc.profiles import RValueProfile
from bytelang.abc.profiles import TypeProfile
from bytelang.abc.registry import MutableRegistry
from bytelang.impl.semantizer.common import CommonSemanticContext
from bytelang.impl.semantizer.super import SuperSemanticContext


class CompositeSemanticContext[T](SuperSemanticContext[T], ABC):
    """Составной контекст семантического анализа"""

    def __init__(self, common: CommonSemanticContext) -> None:
        self._common: Final = common
        """Общий контекст"""

    def getConstants(self) -> MutableRegistry[str, RValueProfile]:
        return self._common.getConstants()

    def getMacros(self) -> MutableRegistry[str, MacroProfile]:
        return self._common.getMacros()

    def getTypes(self) -> MutableRegistry[str, TypeProfile]:
        return self._common.getTypes()
