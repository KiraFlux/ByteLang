from abc import ABC

from bytelang.abc.semantic import SemanticContext
from bytelang.impl.node.super import SuperNode


class Statement[S: SemanticContext](SuperNode[S, None, 'Statement'], ABC):
    """Statement"""
