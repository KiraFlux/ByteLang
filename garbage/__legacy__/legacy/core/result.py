"""Аналог Result из Rust, подогнанный под нужны компилятора"""
from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Optional

from bytelang.core.stream import CollectionInputStream
from bytelang.core.stream import OutputStream
from bytelang.core.stream import SingleOutputStream
from rustpy.exceptions import Panic


def _pass[V](x: V) -> V:
    return x


class _BasicResult[T, E](ABC):
    @abstractmethod
    def map[U](self, f: Callable[[Iterable[T]], U]) -> Result[U, E]:
        """Преобразовать значение результата"""

    @abstractmethod
    def isOk(self) -> bool:
        """Результат является значением"""

    def isErr(self) -> bool:
        """Результат является ошибкой"""
        return not self.isOk()


@dataclass(frozen=True, kw_only=True)
class Result[T, E](_BasicResult[T, E]):
    """Result"""

    _is_ok: bool
    _value: T | E

    def isOk(self) -> bool:
        """Результат является значением"""
        return self._is_ok

    def ok(self) -> Optional[T]:
        """Result[T, E] -> Optional[T]"""
        return self._value if self.isOk() else None

    def err(self) -> Optional[E]:
        """Result[T, E] -> Optional[E]"""
        return self._value if self.isErr() else None

    def map[U](self, f: Callable[[T], U] = _pass) -> Result[U, E]:
        return Ok(f(self._value)) if self.isOk() else self

    def andThen[U](self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Комбинатор And Then"""
        return f(self._value) if self.isOk() else self

    def mapErr[F](self, f: Callable[[E], F]) -> Result[T, F]:
        """Преобразовать ошибку"""
        return Err(f(self._value)) if self.isErr() else self

    def unwrap(self) -> T:
        """Развернуть значение"""

        if self.isOk():
            return self._value

        raise Panic(f"Attempt to unwrap an error: {self}")


def Ok[T](value: T) -> Result[T, Any]:
    """Создать результат со значением"""
    return Result(_is_ok=True, _value=value)


def Err[E](error: E) -> Result[Any, E]:
    """Создать результат с ошибкой"""
    return Result(_is_ok=False, _value=error)


type LogResult[T] = Result[T, OutputStream[str]]


def ErrOne[T](error: str) -> LogResult[T]:
    """Создать единичную ошибку"""
    return Err(SingleOutputStream(error))


class ResultAccumulator[T, E](_BasicResult[T, OutputStream[E]]):
    """Аккумулятор результатов"""

    def map[U](self, f: Callable[[Iterable[T]], U] = _pass) -> Result[U, OutputStream[E]]:
        return Ok(f(self._items.getItems())) if self.isOk() else Err(self._errors)

    def isOk(self) -> bool:
        return len(self._errors.getItems()) == 0

    def put(self, result: Result[T, OutputStream[E]]) -> Result[T, OutputStream[E]]:
        """Поместить результат"""

        if result.isOk():
            self._items.put(result.unwrap())

        else:
            self._errors.extend(result.err().getItems())

        return result

    def unwrap(self) -> Iterable[T]:
        return self._items.getItems() if self.isOk() else Err(self._errors).unwrap()

    def __init__(self) -> None:
        self._errors = CollectionInputStream[E](list())
        self._items = CollectionInputStream[T](list())
