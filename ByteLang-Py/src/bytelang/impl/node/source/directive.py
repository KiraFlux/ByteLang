"""Узлы АСД, используемые только в исполняемой программе (source)"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final
from typing import Iterable
from typing import Optional

from bytelang.abc.node import Directive
from bytelang.abc.node import Node
from bytelang.abc.parser import Parsable
from bytelang.abc.parser import Parser
from bytelang.abc.registry import Registry
from bytelang.abc.registry import RuntimeRegistry
from bytelang.abc.visitor import Visitor
from bytelang.impl.node.common.expression import Identifier
from rustpy.result import Result
from rustpy.result import SingleResult


@dataclass(frozen=True)
class EnvSelectDirective(Directive, Parsable[Directive]):
    """Директива выбора окружения"""

    env: Identifier
    """Идентификатор окружения"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        return Identifier.parse(parser).map(lambda ok: cls(ok))


class EnvSelectVisitor(Visitor):
    """Посетитель узла выбора окружения"""

    def __init__(self, environment_registry: Registry[Identifier, NotImplemented]) -> None:
        self._environment_registry: Final = environment_registry
        self.env: Optional[NotImplemented] = None

    def visit(self, node: Node) -> Result[Node, Iterable[str]]:
        if isinstance(node, EnvSelectDirective):
            if self.env is not None:
                return SingleResult.error((f"Окружение уже выбрано: {self.env}",))

            if (env := self._environment_registry.get(node.env)) is None:
                return SingleResult.error((f"Окружение не найдено: {env}",))

            self.env = env

        return SingleResult.ok(node)


@dataclass(frozen=True)
class MarkDeclareDirective(Directive, Parsable[Directive]):
    """Директива объявления метки"""

    mark: Identifier
    """Имя метки"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        return Identifier.parse(parser).map(lambda ok: cls(ok))


@dataclass(frozen=True)
class MarkDeclareVisitor(Visitor):
    """Посетитель узла определения меток"""
    mark_registry: RuntimeRegistry[Identifier, NotImplemented]

    def visit(self, node: Node) -> Result[Node, Iterable[str]]:
        if isinstance(node, MarkDeclareDirective):
            if (mark := self.mark_registry.get(node.mark)) is not None:
                return SingleResult.error((f"Метка уже существует: {mark}",))

            self.mark_registry.register(node.mark, NotImplemented)

        return SingleResult.ok(node)
