from typing import Optional

from bytelang.abc.registry import Registry
from bytelang.impl.semantizer.common import CommonSemanticContext


class SourceSemanticContext(CommonSemanticContext):
    """Контекст семантического анализа исполняемого кода"""

    environment_registry: Registry[str, NotImplemented]  # todo Env profile
    """Реестр окружений"""

    selected_environment: Optional[NotImplemented]
    """Выбранное окружение"""
