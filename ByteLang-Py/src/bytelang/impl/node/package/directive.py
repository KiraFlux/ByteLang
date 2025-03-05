"""Узлы АСД применимые только для пакетов (Package)"""
from dataclasses import dataclass
from typing import Iterable

from bytelang.abc.node import Directive
from bytelang.abc.parser import Parsable
from bytelang.abc.parser import Parser
from bytelang.core.tokens import TokenType
from bytelang.impl.node.common.expression import Identifier
from bytelang.impl.node.common.type import Field
from rustpy.result import MultipleErrorsResult
from rustpy.result import Result


@dataclass(frozen=True)
class InstructionDefineDirective(Directive, Parsable[Directive]):
    """Узел определения структуры"""

    id: Identifier
    """Идентификатор инструкции"""
    args: Iterable[Field]
    """Аргументы"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        ret = MultipleErrorsResult()

        _id = ret.putSingle(Identifier.parse(parser))
        args = ret.putMulti(parser.braceArguments(lambda: Field.parse(parser), TokenType.OpenRound, TokenType.CloseRound))

        return ret.make(lambda: cls(_id.unwrap(), args.unwrap()))
