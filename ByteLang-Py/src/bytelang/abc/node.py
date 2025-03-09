"""Абстрактные узлы АСД"""
from abc import ABC
from typing import Final


class Node(ABC):
    """Узел AST"""

    _debug_child_node_intend: Final[int] = 4
    """Отступ дочерних элементов"""

    # @abstractmethod
    # def display(self, level: int = 0) -> str:
    #     """
    #     Отобразить AST
    #
    #     StructDefine {
    #
    #     }
    #     """
