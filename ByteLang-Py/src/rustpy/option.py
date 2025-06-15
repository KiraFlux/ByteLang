from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Callable

from rustpy.exceptions import Panic


@dataclass(kw_only=True, frozen=True)
class Option[T]:
    """Rust-like Option<T>"""
    __value: T | None

    def is_none(self) -> bool:
        """Проверка на отсутствие значения"""
        return self.__value is None

    def is_some(self) -> bool:
        """Проверка на наличие значения"""
        return not self.is_none()

    def unwrap(self) -> T:
        """Извлечь значение (паника при None)"""
        if self.is_some():
            return self.__value
        raise Panic("Called unwrap on a None value")

    def expect(self, message: str) -> T:
        """Извлечь значение с сообщением при панике"""
        if self.is_some():
            return self.__value
        raise Panic(message)

    def unwrap_or(self, default: T) -> T:
        """Извлечь значение или вернуть значение по умолчанию"""
        return self.__value if self.is_some() else default

    def map[U](self, f: Callable[[T], U]) -> Option[U]:
        """Применить функцию к значению, если оно есть"""
        return some(f(self.__value)) if self.is_some() else none()

    def and_then[U](self, f: Callable[[T], Option[U]]) -> Option[U]:
        """Цепочка операций с преобразованием"""
        return f(self.__value) if self.is_some() else none()

    def __repr__(self) -> str:
        return f"some({self.__value})" if self.is_some() else "none"


def some[T](value: T) -> Option[T]:
    """Создать Option со значением"""
    return Option(__value=value)


def none() -> Option[Any]:
    """Создать пустой Option"""
    return Option(__value=None)
