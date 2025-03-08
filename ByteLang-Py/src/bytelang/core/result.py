"""Результат"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable
from typing import Final
from typing import Iterable
from typing import Optional

from rustpy.exceptions import Panic


def _pass(v):
    return v


class Result[T, E](ABC):
    """Аналог Result<T, E> из Rust"""

    @abstractmethod
    def _getValue(self) -> Optional[T]:
        """Получить значение"""

    @abstractmethod
    def getError(self) -> Optional[E]:
        """Получить значение ошибки"""

    @abstractmethod
    def isOk(self) -> bool:
        """Результат является значением"""

    def map[_T, _E](self, ok: Callable[[T], _T] = _pass, err: Callable[[E], _E] = _pass) -> Result[_T, _E]:
        """Преобразовать результат"""
        return SingleResult.ok(ok(self._getValue())) if self.isOk() else SingleResult.error(err(self.getError()))

    def pipe(self, make_if_ok: Callable[[T], Result[T, E]]) -> Result[T, E]:
        """Если данный результат не является ошибкой - создать новый"""
        if self.isOk():
            return make_if_ok(self._getValue())
        return self

    def flow[_T, _E](self, err: Callable[[E], _E] = _pass) -> Result[_T, E]:
        """Перенести ошибку под другой тип значения результата"""
        return SingleResult.error(err(self.getError()))

    def isError(self) -> bool:
        """Результат является ошибкой"""
        return not self.isOk()

    def unwrapOr(self, default: T) -> T:
        """Получить значение или значение по умолчанию"""
        return self._getValue() if self.isOk() else default

    def unwrap(self) -> T:
        """Получить значение или паника"""
        if self.isOk():
            return self._getValue()

        raise Panic(f"Attempted to unwrap an error: {self.getError()}")

    def __repr__(self) -> str:
        return f"Ok({self.unwrap()})" if self.isOk() else f"Err({self.getError()})"


@dataclass(frozen=True, repr=False)
class SingleResult[T, E](Result[T, E]):
    """Результат одного значения"""

    _is_ok: bool

    _value: Optional[T]
    _error: Optional[E]
    type Output = Result[T, E]

    @classmethod
    def error(cls, error: E) -> Output:
        """Создать результат-ошибку"""
        return cls(_is_ok=False, _value=None, _error=error)

    @classmethod
    def ok(cls, value: T) -> Output:
        """Создать результат-ошибку"""
        return cls(_is_ok=True, _value=value, _error=None)

    @classmethod
    def fromOptional(cls, value: Optional[T], err_maker: Callable[[], E], ok_maker: Callable[[T], T] = _pass) -> Output:
        """Создать результат на основе Optional"""
        return cls.error(err_maker()) if value is None else cls.ok(ok_maker(value))

    def isOk(self) -> bool:
        return self._is_ok

    def getError(self) -> Optional[E]:
        return self._error

    def _getValue(self) -> Optional[T]:
        return self._value


# TODO Iterable[E] -> Stream

class MultipleErrorsResult[T, E](Result[T, Iterable[E]]):

    def __init__(self) -> None:
        # TODO stream
        self._errors: Final = list[E]()

    def make(self, ok_maker: Callable[[], T]) -> Result[T, Iterable[E]]:
        """Попытаться создать результат если не было ошибок"""
        if self.isOk():
            return SingleResult.ok(ok_maker())

        return SingleResult.error(self.getError())

    def putSingle(self, result: Result[T, E]) -> Result[T, E]:
        """Вернуть результат или поместить ошибку"""
        if result.isError():
            self.putOptionalError(result.getError())

        return result

    def putOptionalError(self, error: Optional[E]) -> None:
        if error is not None:
            self._errors.append(error)

    def putMulti(self, result: Result[T, Iterable[E]]) -> Result[T, Iterable[E]]:
        """Поместить результат, содержащий множественные ошибки"""
        if result.isError():
            self._errors.extend(result.getError())

        return result

    def getError(self) -> Iterable[E]:
        return self._errors

    def _getValue(self) -> Optional[T]:
        raise NotImplementedError

    def isOk(self) -> bool:
        return len(self._errors) == 0


class ResultAccumulator[T, E](Result[Iterable[T], Iterable[E]]):
    """Аккумулятор результатов"""

    def __init__(self) -> None:
        # TODO stream
        self._errors: Final = list[E]()
        self._results: Final = list[T]()

    def mapSingle(self, ok_maker: Callable[[Iterable[T]], T]) -> Result[T, Iterable[E]]:
        """Попытаться создать результат если не было ошибок"""
        if self.isOk():
            return SingleResult.ok(ok_maker(self._results))

        return SingleResult.error(self.getError())

    def putSingle(self, result: Result[T, E]) -> None:
        """Положить результат в аккумулятор"""
        if result.isOk():
            self._putOk(result.unwrap())
        else:
            self.putOptionalError(result.getError())

    def putMulti(self, result: Result[T, Iterable[E]]) -> None:
        """Поместить результат, содержащий множественные ошибки"""
        if result.isOk():
            self._putOk(result.unwrap())
        else:
            self._errors.extend(result.getError())

    def _putOk(self, value: T) -> None:
        self._results.append(value)

    def putOptionalError(self, error: Optional[E]) -> None:
        """Положить ошибку"""
        if error is not None:
            self._errors.append(error)

    def isOk(self) -> bool:
        return len(self._errors) == 0

    def getError(self) -> Optional[Iterable[E]]:
        return self._errors

    def _getValue(self) -> Optional[Iterable[T]]:
        return self._results
