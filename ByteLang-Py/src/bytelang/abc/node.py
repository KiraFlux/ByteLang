"""Абстрактные узлы АСД"""
from __future__ import annotations

from abc import ABC

from bytelang.abc.semantic import SemanticAcceptor
from bytelang.abc.semantic import SemanticContext

# SemanticAcceptor[S, R],
class Node[S: SemanticContext, R](ABC):
    """Узел AST"""
