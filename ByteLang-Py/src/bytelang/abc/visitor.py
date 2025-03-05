from abc import ABC
from abc import abstractmethod
from typing import Iterable

from bytelang.abc.node import Node
from rustpy.result import Result


class Visitor(ABC):
    """Посетитель узла АСД"""

    @abstractmethod
    def visit(self, node: Node) -> Result[Node, Iterable[str]]:
        """Посетить вершину"""
