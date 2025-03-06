"""Выражения, встречаемые только в source файле"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from bytelang.abc.node import Expression
from bytelang.abc.node import Statement
from bytelang.abc.parser import Parsable
from bytelang.abc.parser import Parser
from bytelang.core.tokens import TokenType
from bytelang.impl.node.expression import Identifier
from rustpy.result import MultipleErrorsResult
from rustpy.result import Result


@dataclass(frozen=True)
class Instruction(Statement, Parsable[Statement]):
    """Узел вызова инструкции"""

    id: Identifier
    """Идентификатор выражения"""
    args: Iterable[Expression]
    """Аргументы"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Instruction, Iterable[str]]:
        """Парсинг инструкций"""
        ret = MultipleErrorsResult()

        _id = ret.putSingle(Identifier.parse(parser))
        args = ret.putMulti(parser.arguments(parser.expression, TokenType.Comma, TokenType.StatementEnd))

        return ret.make(lambda: cls(_id.unwrap(), args.unwrap()))
