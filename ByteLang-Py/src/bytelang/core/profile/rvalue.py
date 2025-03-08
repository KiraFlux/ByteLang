from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Sequence

from bytelang.abc.serializer import Serializable
from bytelang.core.ops import Operator
from bytelang.core.result import Result
from bytelang.core.result import SingleResult
from bytelang.core.profile.type import TypeProfile


@dataclass(frozen=True)
class RValueProfile[T: Serializable](ABC):
    """Профиль правостороннего значения"""

    value: T

    @classmethod
    def new(cls, value: T) -> RValueProfile:
        """Создать спецификацию правостороннего значения"""
        return cls(value)

    @abstractmethod
    def getTypeProfile(self) -> TypeProfile[T]:
        """Получить профиль типа"""

    @abstractmethod
    def applyUnaryOperator(self, op: Operator) -> Result[RValueProfile, str]:
        """Применить данный оператор над значением"""
        return SingleResult.error(f"{self} support not {op}")

    @abstractmethod
    def applyBinaryOperator(self, other: RValueProfile, op: Operator) -> Result[RValueProfile, str]:
        """Применить данный бинарный оператор к значению"""
        return SingleResult.error(f"{self} {op} {other} not valid")


class _NumberRV[T: (int, float)](RValueProfile[T], ABC):

    def applyUnaryOperator(self, op: Operator) -> Result[RValueProfile, str]:
        if op == Operator.Minus:
            return SingleResult.ok(_NumberRV(-self.value))

        return super().applyUnaryOperator(op)

    def applyBinaryOperator(self, other: RValueProfile, op: Operator) -> Result[RValueProfile, str]:
        a = self.value
        b = other.value

        def _make(value: T) -> Result[RValueProfile, str]:
            return SingleResult.ok(self.new(value))

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

    @classmethod
    def new(cls, value: int) -> RValueProfile[int]:
        return super().new(int(value))

    def getTypeProfile(self) -> TypeProfile[int]:
        pass


class FloatRV(_NumberRV[float]):
    """Значение вещественного числа"""


class InitializerListRV[T: Sequence[Serializable]](RValueProfile[T]):
    """Список инициализации"""
