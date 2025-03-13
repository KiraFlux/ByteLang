from typing import Final
from typing import final

from bytelang.abc.profiles import PackageInstructionProfile
from bytelang.core.bundle.package import PackageBundle
from bytelang.impl.registry.immediate import MutableImmediateRegistry
from bytelang.impl.semantizer.common import CommonSemanticContext
from bytelang.impl.semantizer.composite import CompositeSemanticContext


@final
class PackageSemanticContext(CompositeSemanticContext[PackageBundle]):
    """Семантический анализатор пакета"""

    def __init__(self, common: CommonSemanticContext) -> None:
        super().__init__(common)

        self.instruction_registry: Final = MutableImmediateRegistry[str, PackageInstructionProfile](())
        """Реестр инструкций"""

    def toBundle(self) -> PackageBundle:
        return PackageBundle(
            instructions=self.instruction_registry
        )
