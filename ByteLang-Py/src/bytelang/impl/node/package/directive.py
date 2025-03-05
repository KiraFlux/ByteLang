"""Узлы АСД применимые только для пакетов (Package)"""
from dataclasses import dataclass
from typing import Iterable
from typing import Sequence

from bytelang.abc.node import Directive
from bytelang.abc.parser import Parsable
from bytelang.abc.parser import Parser
from bytelang.core.tokens import TokenType
from bytelang.impl.node.common.type import Field
from bytelang.impl.node.common.expression import Identifier
from rustpy.result import Result


@dataclass(frozen=True)
class InstructionDeclareDirective(Directive, Parsable[Directive]):
    """Объявление инструкции"""

    id: Identifier
    """Идентификатор инструкции"""
    args: Sequence[Field]
    """Аргументы"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        errors = list[str]()

        _id = Identifier.parse(parser)

        if _id.isError():
            errors.append(_id.getError())

        args = parser.braceArguments(lambda: Field.parse(parser), TokenType.OpenRound, TokenType.CloseRound)

        if args.isError():
            errors.extend(args.getError())

        return Result.chose_LEGACY(len(errors) == 0, cls(_id.unwrap(), args.unwrap()), errors)
