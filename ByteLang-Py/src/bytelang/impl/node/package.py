"""Узлы АСД применимые только для пакетов (Package)"""
from dataclasses import dataclass
from typing import Iterable
from typing import Sequence

from bytelang.abc.node import Directive
from bytelang.abc.parser import Parser
from bytelang.core.tokens import TokenType
from bytelang.impl.node.common import Field
from bytelang.impl.node.common import Identifier
from bytelang.impl.node.common import ParsableDirective
from rustpy.result import Result


@dataclass(frozen=True)
class InstructionDeclareDirective(ParsableDirective):
    """Объявление инструкции"""

    id: Identifier
    """Идентификатор инструкции"""
    args: Sequence[Field]
    """Аргументы"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        errors = list[str]()

        _id = Identifier.parse(parser.tokens)

        if _id.isError():
            errors.append(_id.getError())

        args = parser.braceArguments(lambda: Field.parse(parser.tokens).map(lambda e: (e,)), TokenType.OpenRound, TokenType.CloseRound)

        if args.isError():
            errors.extend(args.getError())

        return Result.error(errors) if errors else Result.ok(cls(_id.unwrap(), args.unwrap()))
