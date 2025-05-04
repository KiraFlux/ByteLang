from abc import ABC

from bytelang.legacy.abc.semantic import SemanticContext
from bytelang.legacy.impl.node.super import SuperNode


class Statement[S: SemanticContext](SuperNode[S, None, 'Statement'], ABC):
    """Statement"""
