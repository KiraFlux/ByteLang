"""Узлы АСД, используемые только в исполняемой программе (source)"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from bytelang.abc.node import Directive
from bytelang.abc.parser import Parser
from bytelang.impl.node.common.expression import Identifier
from bytelang.impl.node.common.directive import ParsableDirective
from rustpy.result import Result


@dataclass(frozen=True)
class EnvSelectDirective(ParsableDirective):
    """Директива выбора окружения"""

    env: Identifier
    """Идентификатор окружения"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        env = Identifier.parse(parser.tokens)

        if env.isError():
            return Result.error((env.getError(),))

        return Result.ok(cls(env.unwrap()))


@dataclass(frozen=True)
class MarkDeclareDirective(ParsableDirective):
    """Директива объявления метки"""
    mark: Identifier
    """Имя метки"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        mark = Identifier.parse(parser.tokens)

        if mark.isError():
            return Result.error((mark.getError(),))

        return Result.ok(cls(mark.unwrap()))
