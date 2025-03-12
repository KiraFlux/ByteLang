from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from bytelang.core.LEGACY_result import LEGACY_Result
from bytelang.core.LEGACY_result import LEGACYResultAccumulator
from bytelang.impl.node.super import SuperNode


@dataclass(frozen=True)
class HasUniqueArguments[T: SuperNode]:
    """Узел имеет уникальные аргументы"""

    arguments: Iterable[T]
    """Аргументы узла"""

    def checkArguments(self) -> LEGACY_Result[Iterable[T], Iterable[str]]:
        """Проверить аргументы на уникальность"""
        ret = LEGACYResultAccumulator()
        used_args = set[T]()

        for arg in self.arguments:
            if arg in used_args:
                ret.putOptionalError(f"Argument already declared: {arg} ({self.arguments})")

            used_args.add(arg)

        return ret
