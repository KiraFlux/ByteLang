"""Реализация реестра мгновенной загрузки"""
from abc import ABC
from abc import abstractmethod
from pathlib import Path
from typing import Iterable

from bytelang.abc.registry import MutableRegistry
from bytelang.abc.registry import Registry
from bytelang.core.result import Result
from bytelang.core.result import SingleResult


class ImmediateRegistry[Key, Item](Registry[Key, Item, str]):
    """Мгновенный реестр - загрузка происходит сразу"""

    def __init__(self, items: Iterable[tuple[Key, Item]]) -> None:
        super().__init__()
        self._items.update(items)

    def get(self, key: Key) -> Result[Item, str]:
        return SingleResult.fromOptional(self._items.get(key), lambda: f"{key} not existing in {self}")


class FileRegistry[Item, RawItem](ImmediateRegistry[str, Item], ABC):
    """Файл-Реестр - загрузка данных из одного файла"""

    def __init__(self, path: Path) -> None:
        super().__init__(self._parseFile(path))

    @abstractmethod
    def _parseFile(self, path: Path) -> Iterable[tuple[str, Item]]:
        """Преобразовать содержимое файла в последовательность пар ключ - предмет"""


class MutableImmediateRegistry[Key, Item](MutableRegistry[Key, Item, str], ImmediateRegistry[Key, Item], ABC):
    """Реестр мгновенной загрузки, изменяемый"""
