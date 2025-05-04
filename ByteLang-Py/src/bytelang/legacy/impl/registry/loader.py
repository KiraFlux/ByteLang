from pathlib import Path

from bytelang.legacy.abc.registry import CatalogRegistry
from bytelang.legacy.abc.semantic import SemanticContext
from bytelang.legacy.core.loader import Loader
from bytelang.legacy.core.result import ErrOne
from bytelang.legacy.core.result import LogResult


class BundleLoaderRegistry[T, S: SemanticContext](CatalogRegistry[T]):
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
