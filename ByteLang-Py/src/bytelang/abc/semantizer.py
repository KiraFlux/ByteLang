"""Семантический анализатор"""
from abc import ABC
from abc import abstractmethod
from typing import Iterable

from bytelang.abc.node import Program
from rustpy.result import Result


class SemantizerContext:
    """Контекст семантического анализатора"""


class SemanticVisitor[T: SemantizerContext](ABC):
    """Посетитель узлов и контекста"""

    @abstractmethod
    def visit(self, node: Program, context: T) -> Result[Program, Iterable[str]]:
        """Посетить узел программы"""
