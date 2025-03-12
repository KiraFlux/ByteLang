"""Реализация RV профиля"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Sequence

from bytelang.abc.profiles import RValueProfile
from bytelang.core.ops import Operator
from bytelang.core.LEGACY_result import LEGACY_Result
from bytelang.core.LEGACY_result import SingleLEGACYResult


@dataclass(frozen=True)
class _NumberRV[T: (int, float)](RValueProfile[T], ABC):
    value: T

    def applyUnaryOperator(self, op: Operator) -> LEGACY_Result[RValueProfile[T], str]:
        if op == Operator.Minus:
            return SingleLEGACYResult.ok(_NumberRV(-self.value))

        return super().applyUnaryOperator(op)

    def applyBinaryOperator(self, other: RValueProfile[T], op: Operator) -> LEGACY_Result[RValueProfile[T], str]:
        a = self.value
        b = other.getValue()

        def _make(value: T) -> LEGACY_Result[RValueProfile[T], str]:
            return SingleLEGACYResult.ok(self.new(value))

        match op:
            case Operator.Plus:
                return _make(a + b)

            case Operator.Minus:
                return _make(a - b)

            case Operator.Star:
                return _make(a * b)

            case Operator.Slash:
                if b == 0:
                    return SingleLEGACYResult.error(f"divide by 0 {other}")
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


class InitializerListRV[T: Sequence](RValueProfile[T]):
    """Список инициализации"""
