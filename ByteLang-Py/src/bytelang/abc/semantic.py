"""Семантический анализатор"""
from abc import ABC
from abc import abstractmethod
from typing import Iterable

from rustpy.result import Result


class SemanticContext(ABC):
    """Контекст семантического анализа"""


class SemanticAcceptor[S: SemanticContext, R](ABC):
    """Узел способный взаимодействовать с контекстом семантического анализатора"""

    @abstractmethod
    def accept(self, context: S) -> Result[R, Iterable[str]]:
        """Использовать контекст на данном"""
