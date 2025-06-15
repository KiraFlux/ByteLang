"""Реализация RV профиля"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Sequence

from bytelang.legacy.abc.profiles import RValueProfile
from bytelang.core.ops import Operator
from bytelang.legacy.core.result import ErrOne
from bytelang.legacy.core.result import LogResult
from bytelang.legacy.core.result import Ok


@dataclass(frozen=True)
class _NumberRV[T: (int, float)](RValueProfile[T], ABC):
    value: T

    def applyUnaryOperator(self, op: Operator) -> LogResult[RValueProfile[T]]:
        if op == Operator.Minus:
            return Ok(_NumberRV(-self.value))

        return super().applyUnaryOperator(op)

    def applyBinaryOperator(self, other: RValueProfile[T], op: Operator) -> LogResult[RValueProfile[T]]:
        a = self.value
        b = other.getValue()

        def _make(value: T) -> LogResult[RValueProfile[T], str]:
            return Ok(self.new(value))

        match op:
            case Operator.Plus:
                return _make(a + b)

            case Operator.Minus:
                return _make(a - b)

            case Operator.Star:
                return _make(a * b)

            case Operator.Slash:
                if b == 0:
                    return ErrOne(f"divide by 0 {other}")
                return _make(a / b)

        return super().applyBinaryOperator(other, op)

    def getValue(self) -> T:
        return self.value


class IntegerRV(_NumberRV[int]):
    """Значение целого числа"""

    @classmethod
    def new(cls, value: int) -> RValueProfile[int]:
        return cls(value)


class FloatRV(_NumberRV[float]):
    """Значение вещественного числа"""

    @classmethod
    def new(cls, value: float) -> RValueProfile[float]:
        return cls(float(value))


@dataclass(frozen=True)
class InitializerListRV[T: Sequence](RValueProfile[T]):
    """Список инициализации"""

    items: T
    """Элементы списка инициализации"""

    @classmethod
    def new(cls, value: T) -> RValueProfile[T]:
        return cls(value)

    def getValue(self) -> T:
        return self.items

    def applyUnaryOperator(self, op: Operator) -> LogResult[RValueProfile[T]]:
        return super().applyUnaryOperator(op)

    def applyBinaryOperator(self, other: RValueProfile[T], op: Operator) -> LogResult[RValueProfile[T]]:
        return super().applyBinaryOperator(other, op)
