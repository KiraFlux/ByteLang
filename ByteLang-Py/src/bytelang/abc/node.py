"""Абстрактные узлы АСД"""
from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Final
from typing import Sequence


class Node(ABC):
    """Узел AST"""

    _debug_display_indent: Final[int] = 4
    """Отступ дочерних узлов"""


class Expression(Node, ABC):
    """Узел Выражения"""


class Statement(Node, ABC):
    """Узел Statement"""


class Directive(Statement, ABC):
    """Узел Директивы"""


@dataclass(frozen=True)
class Program(Node):
    """Узел программы"""

    statements: Sequence[Statement]
    """Statements"""
