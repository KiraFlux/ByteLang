from pathlib import Path
from typing import Optional

from bytelang.abc.registry import CatalogRegistry


class CodeLoadingRegistry(CatalogRegistry):
    """Реестр загрузки кода"""

    def _loadFile(self, filepath: Path) -> Optional[None]:
        pass

