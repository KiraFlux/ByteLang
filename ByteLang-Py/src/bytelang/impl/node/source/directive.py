"""Узлы АСД, используемые только в исполняемой программе (source)"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from bytelang.abc.node import Directive
from bytelang.abc.parser import Parsable
from bytelang.abc.parser import Parser
from bytelang.impl.node.common.expression import Identifier
from rustpy.result import Result


@dataclass(frozen=True)
class EnvSelectDirective(Directive, Parsable[Directive]):
    """Директива выбора окружения"""

    env: Identifier
    """Идентификатор окружения"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        return Identifier.parse(parser).map(lambda ok: cls(ok))


@dataclass(frozen=True)
class MarkDeclareDirective(Directive, Parsable[Directive]):
    """Директива объявления метки"""

    mark: Identifier
    """Имя метки"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        return Identifier.parse(parser).map(lambda ok: cls(ok))
