"""Реализация реестра мгновенной загрузки"""
from abc import ABC
from abc import abstractmethod
from pathlib import Path
from typing import Iterable

from bytelang.legacy.abc.registry import MutableRegistry
from bytelang.legacy.abc.registry import Registry
from bytelang.legacy.core.result import ErrOne
from bytelang.legacy.core.result import LogResult
from bytelang.legacy.core.result import Ok


class ImmediateRegistry[Key, Item](Registry[Key, Item]):
    """Мгновенный реестр - загрузка происходит сразу"""

    def __init__(self, items: Iterable[tuple[Key, Item]]) -> None:
        super().__init__()
        self._items.update(items)

    def get(self, key: Key) -> LogResult[Item]:
        ret = self._items.get(key)

        if ret is None:
            return ErrOne(f"{key} not existing in {self}")

        return Ok(ret)


class FileRegistry[Item, RawItem](ImmediateRegistry[str, Item], ABC):
    """Файл-Реестр - загрузка данных из одного файла"""

    def __init__(self, path: Path) -> None:
        super().__init__(self._parseFile(path))

    @abstractmethod
    def _parseFile(self, path: Path) -> Iterable[tuple[str, Item]]:
        """Преобразовать содержимое файла в последовательность пар ключ - предмет"""


class MutableImmediateRegistry[Key, Item](MutableRegistry[Key, Item], ImmediateRegistry[Key, Item], ABC):
    """Реестр мгновенной загрузки, изменяемый"""
