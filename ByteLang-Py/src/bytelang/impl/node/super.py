"""Великий костыль"""
from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Iterable
from typing import Optional

from bytelang.abc.node import Node
from bytelang.abc.parser import Parsable
from bytelang.abc.registry import Registry
from bytelang.abc.semantic import SemanticAcceptor
from bytelang.abc.semantic import SemanticContext
from bytelang.impl.node.expression import Identifier
from rustpy.result import Result
from rustpy.result import ResultAccumulator
from rustpy.result import SingleResult


class SuperNode[S: SemanticContext, R, P: Node](Node, SemanticAcceptor[S, R], Parsable[P], ABC):
    """
    Супер-узел - реализует нужные интерфейсы и является костылем
    S - Уровень контекста семантического анализа
    R - Тип Возвращаемого значения после семантического анализа
    P - Возвращаемый тип после парсинга
    """


@dataclass(frozen=True)
class HasArguments[T: SuperNode, S: SemanticContext]:
    """Узел имеет аргументы"""

    arguments: Iterable[T]
    """Аргументы узла"""

    def checkArguments(self, semantizer: S) -> Result[Iterable[T], Iterable[str]]:
        """Проверить аргументы на уникальность"""
        ret = ResultAccumulator()
        used_args = set[T]()

        for arg in self.arguments:
            if arg in used_args:
                ret.putOptionalError(f"Argument already declared: {arg} ({self.arguments})")

            used_args.add(arg)
            ret.putMulti(arg.accept(semantizer))

        return ret


@dataclass(frozen=True)
class HasIdentifier:
    """Узел имеет идентификатор"""

    identifier: Identifier
    """Идентификатор узла"""


class HasUniqueID(HasIdentifier):
    """Узел имеет уникальный идентификатор"""

    def checkIdentifier[T](self, registry: Registry[Identifier, T]) -> Optional[str]:
        """Проверить уникальность идентификатора"""
        if registry.has(self.identifier):
            return f"{registry} has {self}"


class HasExistingID(HasIdentifier):
    """Узел имеет идентификатор, уже содержащийся в реестре"""

    def checkIdentifier[T](self, registry: Registry[Identifier, T]) -> Result[T, str]:
        """Проверить наличие идентификатора и получить результат"""
        return SingleResult.fromOptional(registry.get(self.identifier), lambda: f"ID{self} not existing in {registry}")
