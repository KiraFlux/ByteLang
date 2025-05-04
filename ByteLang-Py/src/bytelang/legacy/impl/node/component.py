from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from bytelang.legacy.core.result import ErrOne
from bytelang.legacy.core.result import LogResult
from bytelang.legacy.core.result import ResultAccumulator
from bytelang.legacy.impl.node.super import SuperNode


@dataclass(frozen=True)
class HasUniqueArguments[T: SuperNode]:
    """Узел имеет уникальные аргументы"""

    arguments: Iterable[T]
    """Аргументы узла"""

    def checkArguments(self) -> LogResult[Iterable[T]]:
        """Проверить аргументы на уникальность"""
        ret = ResultAccumulator()
        used_args = set[T]()

        for arg in self.arguments:
            if arg in used_args:
                ret.put(ErrOne(f"Argument already declared: {arg} ({self.arguments})"))

            used_args.add(arg)

        return ret.map()
