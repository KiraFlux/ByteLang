from typing import Optional

from bytelang.impl.semantizer.common import CommonSemanticContext


class SourceSemanticContext(CommonSemanticContext):
    """Контекст семантического анализа исполняемого кода"""

    environment_registry: NotImplemented
    selected_environment: Optional[NotImplemented]
    """Выбранное окружение"""
