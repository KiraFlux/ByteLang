"""Реестр"""

from abc import ABC
from abc import abstractmethod
from pathlib import Path
from typing import Final
from typing import Iterable
from typing import Optional


class Registry[Key, Item](ABC):
    """Реестр"""

    def __init__(self) -> None:
        self._items = dict[Key, Item]()

    @abstractmethod
    def get(self, key: Key) -> Optional[Item]:
        """Получить предмет по ключу"""

    def has(self, key: Key) -> bool:
        """Реестр содержит запись"""
        return key in self._items

    def getItems(self) -> Iterable[tuple[Key, Item]]:
        """Получить значения реестра"""
        return self._items.items()


class RuntimeRegistry[Key, Item](Registry, ABC):
    """Интерфейс позволяет добавлять элементы налету"""

    def register(self, key: Key, item: Item) -> None:
        """Зарегистрировать элемент"""
        self._items[key] = item


class ImmediateRegistry[Key, Item](Registry[Key, Item]):
    """Мгновенный реестр - загрузка происходит сразу"""

    def __init__(self, items: Iterable[tuple[Key, Item]]) -> None:
        super().__init__()
        self._items.update(items)

    def get(self, key: Key) -> Optional[Item]:
        return self._items.get(key)


class LazyRegistry[Key, Item](Registry[Key, Item]):
    """Ленивый реестр - загрузка происходит по мере необходимости"""

    def get(self, key: Key) -> Optional[Item]:
        if (ret := self._items.get(key)) is not None:
            return ret

        if (ret := self._load(key)) is not None:
            self._items[key] = ret
            return ret

        return None

    @abstractmethod
    def _load(self, key: Key) -> Optional[Item]:
        """Загрузить предмет"""


class FileRegistry[Item, RawItem](ImmediateRegistry[str, Item]):
    """Файл-Реестр - загрузка данных из одного файла"""

    def __init__(self, path: Path) -> None:
        super().__init__(self._parseFile(path))

    @abstractmethod
    def _parseFile(self, path: Path) -> Iterable[tuple[str, Item]]:
        """Преобразовать содержимое файла в последовательность пар ключ - предмет"""


class CatalogRegistry[Item](LazyRegistry[str, Item]):
    """Каталоговый реестр - загрузка файлов по мере необходимости"""

    def __init__(self, catalog: Path, extension: str) -> None:
        super().__init__()
        self._path: Final[Path] = catalog
        self._extension: Final[str] = extension

    @abstractmethod
    def _loadFile(self, filepath: Path) -> Optional[Item]:
        """Загрузить из файла"""

    def _load(self, key: str) -> Optional[Item]:
        return self._loadFile(self.__keyToPath(key))

    def __keyToPath(self, key: str) -> Path:
        return self._path / f"{key}.{self._extension}"
