from __future__ import annotations

from dataclasses import dataclass

from bytelang.abc.profiles import MacroProfile
from bytelang.abc.profiles import RValueProfile
from bytelang.abc.profiles import TypeProfile
from bytelang.abc.registry import MutableRegistry
from bytelang.abc.semantic import SemanticContext


@dataclass
class CommonSemanticContext(SemanticContext[None]):
    """Контекст общего назначения"""

    macro_registry: MutableRegistry[str, MacroProfile, str]
    """Реестр макросов"""

    type_registry: MutableRegistry[str, TypeProfile, str]
    """Реестр типов"""

    const_registry: MutableRegistry[str, RValueProfile, str]
    """Реестр констант"""

    def toBundle(self) -> None:
        return None
