"""Профиль макроса"""
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Sequence

from bytelang.abc.node import Node
from bytelang.core.result import Result


@dataclass(frozen=True)
class MacroProfile[Arg: Node](ABC):
    """Профиль макроса"""

    @abstractmethod
    def expand(self, arguments: Sequence[Arg]) -> Result[Arg, str]:
        """Развернуть макрос"""
