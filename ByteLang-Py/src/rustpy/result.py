from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from typing import Optional

from rustpy.exceptions import Panic


@dataclass(frozen=True)
class Result[T, E]:
    """Аналог Result<T, E> из Rust"""

    type Output = Result[T, E]

    _is_ok: bool
    _value: Optional[T]
    _error: Optional[E]

    @staticmethod
    def _pass[T](v: T):
        return v

    @classmethod
    def error(cls, error: E) -> Output:
        """Создать результат-ошибку"""
        return cls(_is_ok=False, _value=None, _error=error)

    @classmethod
    def ok(cls, value: T) -> Output:
        """Создать результат-ошибку"""
        return cls(_is_ok=True, _value=value, _error=None)

    @classmethod
    def chose_LEGACY(cls, make_ok: bool, value: T, error: E) -> Output:
        """Выбор результата на основе входного значения"""
        return cls.ok(value) if make_ok else cls.error(error)

    def map_LEGACY[OtherErr](self, error_transformer: Callable[[E], OtherErr]) -> Output:
        """Преобразовать результат с ошибкой данного типа в результат ошибки этого типа"""
        return self if self.isOk() else self.error(error_transformer(self.getError()))

    def map[_T, _E](self, ok: Callable[[T], _T] = _pass, err: Callable[[E], _E] = _pass) -> Result[_T, _E]:
        """Преобразовать результат"""
        return self.ok(ok(self.unwrap())) if self.isOk() else self.error(err(self.getError()))

    def isOk(self) -> bool:
        """Результат является значением"""
        return self._is_ok

    def isError(self) -> bool:
        """Результат является ошибкой"""
        return not self.isOk()

    def getError(self) -> Optional[E]:
        """Получить значение ошибки"""
        return self._error

    def unwrapOr(self, default: T) -> T:
        """Получить значение или дефолт если ошибка"""
        return self._value if self.isOk() else default

    def unwrap(self) -> T:
        """Получить значение или паника"""
        if self.isOk():
            return self._value

        raise Panic(f"Attempted to unwrap an error: {self._error}")

    def __str__(self) -> str:
        return f"Ok({self._value})" if self.isOk() else f"Err({self._error})"
