from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable

from bytelang.abc.node import Directive
from bytelang.abc.parser import Parser
from bytelang.impl.node.gamma import Identifier
from rustpy.result import Result


class ParsableDirective(Directive, ABC):
    @classmethod
    @abstractmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        """Преобразовать токены в конкретную директиву"""


@dataclass(frozen=True)
class EnvSelectDirective(ParsableDirective):
    env: Identifier
    """Идентификатор окружения"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        env = Identifier.parse(parser.tokens)

        if env.isError():
            return Result.error((env.getError(),))

        return Result.ok(cls(env.unwrap()))
