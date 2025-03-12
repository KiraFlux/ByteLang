"""Семантический анализатор"""
from abc import ABC
from abc import abstractmethod
from typing import Iterable

from bytelang.core.LEGACY_result import LEGACY_Result


class SemanticContext[T](ABC):
    """Контекст семантического анализа"""

    @abstractmethod
    def toBundle(self) -> T:
        """Преобразовать семантический контекст в набор"""


class SemanticAcceptor[S: SemanticContext, R](ABC):
    """Узел способный взаимодействовать с контекстом семантического анализатора"""

    @abstractmethod
    def accept(self, context: S) -> LEGACY_Result[R, Iterable[str]]:
        """Использовать контекст на данном"""
