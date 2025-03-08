from bytelang.abc.registry import MutableRegistry
from bytelang.impl.semantizer.common import CommonSemanticContext


class PackageSemanticContext(CommonSemanticContext):
    """Семантический анализатор пакета"""

    instructions: MutableRegistry[str, NotImplemented]  # todo instruction Profile
    """Инструкции пакета"""
