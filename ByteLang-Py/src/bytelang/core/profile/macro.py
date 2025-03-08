"""Профиль макроса"""
from abc import ABC
from abc import abstractmethod
from typing import Iterable

from bytelang.abc.node import Node


class MacroProfile[Arg: Node](ABC):
    """Профиль макроса"""

    @abstractmethod
    def expand(self, arguments: Iterable[Arg]) -> Arg:
        """Развернуть макрос"""
