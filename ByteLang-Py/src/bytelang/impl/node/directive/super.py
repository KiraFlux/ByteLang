from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from bytelang.abc.semantic import SemanticContext
from bytelang.impl.node.statement import Statement


class Directive[S: SemanticContext](Statement[S], ABC):
    """Узел Директивы"""

    @classmethod
    @abstractmethod
    def getIdentifier(cls) -> str:
        """Получить идентификатор директивы"""
