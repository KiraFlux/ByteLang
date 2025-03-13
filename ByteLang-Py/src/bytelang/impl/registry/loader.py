from pathlib import Path

from bytelang.abc.registry import CatalogRegistry
from bytelang.abc.semantic import SemanticContext
from bytelang.core.loader import Loader
from bytelang.core.result import ErrOne
from bytelang.core.result import LogResult


class CodeLoadingRegistry[T, S: SemanticContext](CatalogRegistry[T]):
    """Реестр загрузки кода"""

    def __init__(self, catalog: Path, loader: Loader[T, S]) -> None:
        super().__init__(catalog, "bls")
        self._loader = loader

    def _loadFile(self, filepath: Path) -> LogResult[T]:
        try:
            with open(filepath) as source:
                return self._loader.load(source)

        except OSError as e:
            return ErrOne(f"Cannot open {filepath}: {e}")
