"""Реестр"""

from abc import ABC
from abc import abstractmethod
from pathlib import Path
from typing import Final
from typing import Iterable
from typing import Mapping

from bytelang.core.result import Result


class Registry[Key, Item, Err](ABC):
    """Реестр"""

    def __init__(self) -> None:
        self._items = dict[Key, Item]()

    @abstractmethod
    def get(self, key: Key) -> Result[Item, Err]:
        """Получить предмет по ключу"""

    def has(self, key: Key) -> bool:
        """Реестр содержит запись"""
        return key in self._items

    def getItems(self) -> Iterable[tuple[Key, Item]]:
        """Получить значения реестра"""
        return self._items.items()

    def getMappingView(self) -> Mapping[Key, Item]:
        """Получить вид на элементы"""
        return self._items


class MutableRegistry[Key, Item, Err](Registry[Key, Item, Err], ABC):
    """Интерфейс позволяет добавлять элементы налету"""

    def register(self, key: Key, item: Item) -> None:
        """Зарегистрировать элемент"""
        self._items[key] = item

    def extend(self, items: Iterable[tuple[Key, Item]]):
        """Расширить значения реестра"""
        self._items.update(items)


class LazyRegistry[Key, Item, Err](Registry[Key, Item, Err], ABC):
    """Ленивый реестр - загрузка происходит по мере необходимости"""

    def get(self, key: Key) -> Result[Item, Err]:
        if (ret := self._items.get(key)) is not None:
            return ret

        ret = self._load(key)

        if ret.isOk():
            self._items[key] = ret.unwrap()

        return ret

    @abstractmethod
    def _load(self, key: Key) -> Result[Item, Err]:
        """Загрузить предмет"""


class CatalogRegistry[Item, Err](LazyRegistry[str, Item, Err], ABC):
    """Каталоговый реестр - загрузка файлов по мере необходимости"""

    def __init__(self, catalog: Path, extension: str) -> None:
        super().__init__()
        self._path: Final[Path] = catalog
        self._extension: Final[str] = extension

    @abstractmethod
    def _loadFile(self, filepath: Path) -> Result[Item, Err]:
        """Загрузить из файла"""

    def _load(self, key: str) -> Result[Item, Err]:
        return self._loadFile(self.__keyToPath(key))

    def __keyToPath(self, key: str) -> Path:
        return self._path / f"{key}.{self._extension}"
