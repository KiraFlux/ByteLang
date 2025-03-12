from dataclasses import dataclass
from typing import Final
from typing import Iterable
from typing import MutableSequence
from typing import Optional
from typing import Sequence

from bytelang.abc.stream import InputStream
from bytelang.abc.stream import OutputStream


@dataclass
class CollectionInputStream[T](InputStream[T]):
    """Поток входа (для записи)"""

    _items: MutableSequence[T]

    def put(self, item: T) -> None:
        """Поместить элемент"""
        self._items.append(item)

    def extend(self, items: Iterable[T]) -> None:
        """Добавить элементы"""
        self._items.extend(items)

    def getItems(self) -> Sequence[T]:
        """Получить последовательность элементов"""
        return self._items


class CollectionOutputStream[T](OutputStream[T]):
    """Поток выхода на основе коллекции"""

    def __init__(self, items: Sequence[T]) -> None:
        self._items: Final = items
        self._position = 0

    def peek(self) -> Optional[T]:
        if self._position < len(self._items):
            return self._items[self._position]

    def next(self) -> Optional[T]:
        ret = self.peek()
        self._position += 1
        return ret


class SingleOutputStream[T](OutputStream[T]):
    """Потом выхода из одного элемента"""

    def next(self) -> Optional[T]:
        ret = self._item
        self._item = None
        return ret

    def peek(self) -> Optional[T]:
        return self._item

    def __init__(self, item: T) -> None:
        self._item: Optional[T] = item
