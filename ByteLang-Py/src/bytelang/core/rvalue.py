from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Sequence

from bytelang.abc.serializer import Serializable
from bytelang.core.tokens import Operator
from bytelang.core.type import TypeProfile
from rustpy.result import Result
from rustpy.result import SingleResult


@dataclass(frozen=True)
class RValueSpec[T: Serializable](ABC):
    """Спецификация правостороннего значения"""

    value: T

    @classmethod
    def new(cls, value: T) -> RValueSpec:
        """Создать спецификацию правостороннего значения"""
        return cls(value)

    @abstractmethod
    def getTypeProfile(self) -> TypeProfile[T]:
        """Получить профиль типа"""

    @abstractmethod
    def applyUnaryOperator(self, op: Operator) -> Result[RValueSpec, str]:
        """Применить данный оператор над значением"""
        return SingleResult.error(f"{self} support not {op}")

    @abstractmethod
    def applyBinaryOperator(self, other: RValueSpec, op: Operator) -> Result[RValueSpec, str]:
        """Применить данный бинарный оператор к значению"""
        return SingleResult.error(f"{self} {op} {other} not valid")


class _NumberRV[T: (int, float)](RValueSpec[T]):

    def applyUnaryOperator(self, op: Operator) -> Result[RValueSpec, str]:
        if op == Operator.Minus:
            return SingleResult.ok(_NumberRV(-self.value))

        return super().applyUnaryOperator(op)

    def applyBinaryOperator(self, other: RValueSpec, op: Operator) -> Result[RValueSpec, str]:
        a = self.value
        b = other.value

        def _make(value: T):
            return SingleResult.ok(value)

        match op:
            case Operator.Plus:
                return _make(a + b)

            case Operator.Minus:
                return _make(a - b)

            case Operator.Star:
                return _make(a * b)

            case Operator.Slash:
                if b == 0:
                    return SingleResult.error(f"divide by 0 {other}")
                return _make(a / b)

        return super().applyBinaryOperator(other, op)


class IntegerRV(_NumberRV[int]):
    """Значение целого числа"""


class FloatRV(_NumberRV[float]):
    """Значение вещественного числа"""


class InitializerListRV[T: Sequence[Serializable]](RValueSpec[T]):
    """Список инициализации"""
