from dataclasses import dataclass

from bytelang.abc.semantizer import SemantizerContext
from bytelang.impl.node.expression import Identifier
from bytelang.impl.registry.immediate import RuntimeImmediateRegistry


@dataclass(frozen=True)
class CommonSemantizerContext(SemantizerContext):
    """Обобщенный контекст семантического анализатора"""

    type_registry: RuntimeImmediateRegistry[Identifier, NotImplemented]
    """Реестр типов"""

    const_registry: RuntimeImmediateRegistry[Identifier, NotImplemented]
    """Реестр констант"""
