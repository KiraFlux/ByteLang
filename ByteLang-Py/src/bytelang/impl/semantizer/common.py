from __future__ import annotations

from typing import final

from bytelang.abc.profiles import MacroProfile
from bytelang.abc.profiles import RValueProfile
from bytelang.abc.profiles import TypeProfile
from bytelang.abc.registry import MutableRegistry
from bytelang.impl.registry.immediate import MutableImmediateRegistry
from bytelang.impl.registry.primitive import PrimitiveRegistry
from bytelang.impl.semantizer.super import SuperSemanticContext


@final
class CommonSemanticContext(SuperSemanticContext[NotImplemented]):
    """Контекст общего назначения"""

    def __init__(self, primitives: PrimitiveRegistry) -> None:
        self._type_registry = self._makeTypeRegistry(primitives)
        """Реестр типов"""

        self._macro_registry = MutableImmediateRegistry[str, MacroProfile](())
        """Реестр макросов"""

        self._const_registry = MutableImmediateRegistry[str, RValueProfile](())
        """Реестр констант"""

    @staticmethod
    def _makeTypeRegistry(primitives: PrimitiveRegistry) -> MutableRegistry[str, TypeProfile]:
        from bytelang.impl.profiles.type import PrimitiveTypeProfile

        return MutableImmediateRegistry[str, TypeProfile]((
            (key, PrimitiveTypeProfile(item))
            for key, item in primitives.getMappingView().items()
        ))

    def getConstants(self) -> MutableRegistry[str, RValueProfile]:
        return self._const_registry

    def getMacros(self) -> MutableRegistry[str, MacroProfile]:
        return self._macro_registry

    def getTypes(self) -> MutableRegistry[str, TypeProfile]:
        return self._type_registry

    def toBundle(self) -> NotImplemented:
        raise NotImplementedError
