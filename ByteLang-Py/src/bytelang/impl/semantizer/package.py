from dataclasses import dataclass

from bytelang.abc.profiles import PackageInstructionProfile
from bytelang.abc.registry import MutableRegistry
from bytelang.abc.semantic import SemanticContext
from bytelang.core.bundle.package import PackageBundle
from bytelang.impl.semantizer.common import CommonSemanticContext


@dataclass
class PackageSemanticContext(CommonSemanticContext, SemanticContext[PackageBundle]):
    """Семантический анализатор пакета"""

    instruction_registry: MutableRegistry[str, PackageInstructionProfile]
    """Реестр инструкций"""

    def toBundle(self) -> PackageBundle:
        return PackageBundle(
            instructions=self.instruction_registry
        )
