"""Узлы АСД, используемые только в исполняемой программе (source)"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from typing import Sequence

from bytelang.abc.node import Directive
from bytelang.abc.node import Expression
from bytelang.abc.node import Statement
from bytelang.abc.parser import Parser
from bytelang.core.tokens import TokenType
from bytelang.impl.node.common import Identifier
from bytelang.impl.node.common import ParsableDirective
from rustpy.result import Result


@dataclass(frozen=True)
class Instruction(Statement):
    """Узел вызова инструкции"""

    id: Identifier
    """Идентификатор выражения"""
    args: Sequence[Expression]
    """Аргументы"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Instruction, Iterable[str]]:
        """Парсинг инструкций"""
        errors = list[str]()

        id_result = Identifier.parse(parser.tokens)

        if id_result.isError():
            errors.append(id_result.getError())

        args = parser.arguments(TokenType.Comma)

        if args.isError():
            errors.extend(args.getError())

        return Result.error(errors) if errors else Result.ok(Instruction(id_result.unwrap(), args.unwrap()))


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
