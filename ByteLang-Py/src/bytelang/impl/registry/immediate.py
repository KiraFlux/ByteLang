"""Реализация реестра мгновенной загрузки"""
from abc import abstractmethod
from pathlib import Path
from pathlib import Path

from typing import Iterable
from typing import Iterable
from typing import Optional

from bytelang.abc.registry import Registry


class ImmediateRegistry[Key, Item](Registry[Key, Item]):
    """Мгновенный реестр - загрузка происходит сразу"""

    def __init__(self, items: Iterable[tuple[Key, Item]]) -> None:
        super().__init__()
        self._items.update(items)

    def get(self, key: Key) -> Optional[Item]:
        return self._items.get(key)


class FileRegistry[Item, RawItem](ImmediateRegistry[str, Item]):
    """Файл-Реестр - загрузка данных из одного файла"""

    def __init__(self, path: Path) -> None:
        super().__init__(self._parseFile(path))

    @abstractmethod
    def _parseFile(self, path: Path) -> Iterable[tuple[str, Item]]:
        """Преобразовать содержимое файла в последовательность пар ключ - предмет"""
