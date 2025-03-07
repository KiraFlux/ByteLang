from dataclasses import dataclass

from bytelang.abc.semantic import SemanticContext
from bytelang.core.rvalue import RValueSpec
from bytelang.core.type import TypeProfile
from bytelang.impl.node.directive import MacroDefine
from bytelang.impl.node.expression import Identifier
from bytelang.impl.registry.immediate import RuntimeImmediateRegistry


@dataclass
class CommonSemanticContext(SemanticContext):
    """Контекст общего назначения"""

    type_registry: RuntimeImmediateRegistry[Identifier, TypeProfile]
    """Реестр типов"""

    const_registry: RuntimeImmediateRegistry[Identifier, RValueSpec]
    """Реестр констант"""

    macro_registry: RuntimeImmediateRegistry[Identifier, MacroDefine]
    """Реестр макросов"""
