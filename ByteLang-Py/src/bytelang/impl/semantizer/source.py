from dataclasses import dataclass
from typing import Optional

from bytelang.abc.registry import Registry
from bytelang.impl.semantizer.common import CommonSemanticContext


@dataclass
class SourceSemanticContext(CommonSemanticContext):
    """Контекст семантического анализа исполняемого кода"""

    environment_registry: Registry[str, NotImplemented, NotImplemented]  # todo Env bundle
    """Реестр окружений"""

    selected_environment: Optional[NotImplemented]
    """Выбранное окружение"""
