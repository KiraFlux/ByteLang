from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from typing import Sequence

from bytelang.abc.node import Expression
from bytelang.abc.node import Statement
from bytelang.abc.parser import Parsable
from bytelang.abc.parser import Parser
from bytelang.core.tokens import TokenType
from bytelang.impl.node.common.expression import Identifier
from rustpy.result import Result


@dataclass(frozen=True)
class Instruction(Statement, Parsable[Statement]):
    """Узел вызова инструкции"""

    id: Identifier
    """Идентификатор выражения"""
    args: Sequence[Expression]
    """Аргументы"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Instruction, Iterable[str]]:
        """Парсинг инструкций"""
        errors = list[str]()

        id_result = Identifier.parse(parser)

        if id_result.isError():
            errors.extend(id_result.getError())

        args = parser.arguments(parser.expression, TokenType.Comma, TokenType.StatementEnd)

        if args.isError():
            errors.extend(args.getError())

        return Result.chose_LEGACY(len(errors) == 0, Instruction(id_result.unwrap(), args.unwrap()), errors)
