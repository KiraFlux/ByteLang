from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from rustpy.exceptions import Panic


@dataclass(frozen=True)
class Result[T, E]:
    """Аналог Result<T, E> из Rust"""

    type Output = Result[T, E]

    _is_ok: bool
    _value: Optional[T]
    _error: Optional[E]

    @classmethod
    def error(cls, error: E) -> Output:
        """Создать результат-ошибку"""
        return cls(_is_ok=False, _value=None, _error=error)

    @classmethod
    def ok(cls, value: T) -> Output:
        """Создать результат-ошибку"""
        return cls(_is_ok=True, _value=value, _error=None)

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
