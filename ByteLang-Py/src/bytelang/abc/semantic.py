"""Семантический анализатор"""
from abc import ABC
from abc import abstractmethod

from bytelang.core.result import LogResult


class SemanticContext[T](ABC):
    """Контекст семантического анализа"""

    @abstractmethod
    def toBundle(self) -> T:
        """Преобразовать семантический контекст в набор"""


class SemanticAcceptor[S: SemanticContext, R](ABC):
    """Узел способный взаимодействовать с контекстом семантического анализатора"""

    @abstractmethod
    def accept(self, context: S) -> LogResult[R]:
        """Использовать контекст на данном"""
