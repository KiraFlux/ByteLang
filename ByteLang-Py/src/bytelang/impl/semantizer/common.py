from dataclasses import dataclass

from bytelang.abc.semantic import SemanticContext
from bytelang.impl.node.expression import Identifier
from bytelang.impl.registry.immediate import RuntimeImmediateRegistry


@dataclass(frozen=True)
class CommonSemanticContext(SemanticContext):
    """Контекст общего назначения"""

    type_registry: RuntimeImmediateRegistry[Identifier, NotImplemented]
    """Реестр типов"""
    const_registry: RuntimeImmediateRegistry[Identifier, NotImplemented]
    """Реестр констант"""
