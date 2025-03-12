from pathlib import Path
from typing import Iterable

from bytelang.abc.registry import CatalogRegistry
from bytelang.abc.semantic import SemanticContext
from bytelang.core.loader import Loader
from bytelang.core.LEGACY_result import LEGACY_Result
from bytelang.core.LEGACY_result import SingleLEGACYResult


class CodeLoadingRegistry[Bnd, S: SemanticContext](CatalogRegistry[Bnd, Iterable[str]]):
    """Реестр загрузки кода"""

    def __init__(self, catalog: Path, loader: Loader[Bnd, S]) -> None:
        super().__init__(catalog, "bls")
        self._loader = loader

    def _loadFile(self, filepath: Path) -> LEGACY_Result[Bnd, Iterable[str]]:
        try:
            with open(filepath) as source:
                return self._loader.load(source)

        except OSError as e:
            return SingleLEGACYResult.error(f"Cannot open {filepath}: {e}")
