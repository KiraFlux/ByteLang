from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable
from typing import Sequence

from bytelang.abc.node import Node
from bytelang.abc.semantic import SemanticContext
from bytelang.core.ops import Operator
from bytelang.core.result import Result


@dataclass(frozen=True)
class MacroProfile[Arg: Node](ABC):
    """Профиль макроса"""

    @abstractmethod
    def expand(self, arguments: Sequence[Arg]) -> Result[Arg, str]:
        """Развернуть макрос"""


class RValueProfile[T](ABC):
    """Профиль правостороннего значения"""

    @classmethod
    @abstractmethod
    def new[T](cls, value: T) -> RValueProfile[T]:
        """Создать профиль правостороннего значения"""

    @abstractmethod
    def getValue(self) -> T:
        """Получить значение профиля"""

    @abstractmethod
    def applyUnaryOperator(self, op: Operator) -> Result[RValueProfile[T], str]:
        """Применить данный оператор над значением"""

    @abstractmethod
    def applyBinaryOperator(self, other: RValueProfile[T], op: Operator) -> Result[RValueProfile[T], str]:
        """Применить данный бинарный оператор к значению"""


class TypeProfile[S: SemanticContext](ABC):
    """Профиль типа"""

    @abstractmethod
    def apply[T](self, rvalue: RValueProfile[T], context: S) -> Result[bytes, Iterable[str]]:
        """Применить профиль типа на rvalue"""
