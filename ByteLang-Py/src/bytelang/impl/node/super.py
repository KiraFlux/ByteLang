"""Великий костыль"""
from __future__ import annotations

from abc import ABC

from bytelang.abc.node import Node
from bytelang.abc.parser import Parsable
from bytelang.abc.semantic import SemanticAcceptor
from bytelang.abc.semantic import SemanticContext


class SuperNode[S: SemanticContext, R, P: Node](Node, SemanticAcceptor[S, R], Parsable[P], ABC):
    """
    Супер-узел - реализует нужные интерфейсы и является костылем
    S - Уровень контекста семантического анализа
    R - Тип Возвращаемого значения после семантического анализа
    P - Возвращаемый тип после парсинга
    """
