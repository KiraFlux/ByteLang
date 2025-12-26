from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Callable

from rustpy.exceptions import Panic
from rustpy.option import Option
from rustpy.option import none
from rustpy.option import some


@dataclass(frozen=True, kw_only=True)
class Result[T, E]:
    """Result"""
    _is_ok: bool
    _value: T | E

    def is_ok(self) -> bool:
        """Проверка на успешный результат"""
        return self._is_ok

    def is_err(self) -> bool:
        """Проверка на ошибку"""
        return not self.is_ok()

    def ok(self) -> Option[T]:
        """Преобразовать в Option<T> (значение)"""
        return some(self._value) if self.is_ok() else none()

    def err(self) -> Option[E]:
        """Преобразовать в Option<E> (ошибка)"""
        return some(self._value) if self.is_err() else none()

    def map[U](self, f: Callable[[T], U]) -> Result[U, E]:
        """Преобразовать успешное значение"""
        return ok(f(self._value)) if self.is_ok() else self

    def map_err(self, f: Callable[[E], Any]) -> Result[T, Any]:
        """Преобразовать ошибку"""
        return err(f(self._value)) if self.is_err() else self

    def and_then[U](self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Цепочка операций с преобразованием"""
        return f(self._value) if self.is_ok() else self

    def unwrap(self) -> T:
        """Извлечь значение (паника при ошибке)"""
        if self.is_ok():
            return self._value
        raise Panic(f"Attempt to unwrap an error: {self}")

    def unwrap_or(self, default: T) -> T:
        """Извлечь значение или вернуть значение по умолчанию"""
        return self._value if self.is_ok() else default

    def __repr__(self) -> str:
        return f"{self.__get_repr_str()}({self._value})"

    def __get_repr_str(self) -> str:
        return "ok" if self.is_ok() else "err"


def ok[T](value: T) -> Result[T, Any]:
    """Создать успешный результат"""
    return Result(_is_ok=True, _value=value)


def err[E](error: E) -> Result[Any, E]:
    """Создать результат с ошибкой"""
    return Result(_is_ok=False, _value=error)
