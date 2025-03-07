"""Выражения, встречаемые только в source файле"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from bytelang.abc.parser import Parser
from bytelang.core.tokens import TokenType
from bytelang.impl.node.expression import Expression
from bytelang.impl.node.expression import Identifier
from bytelang.impl.node.statement import Statement
from bytelang.impl.semantizer.package import PackageSemanticContext
from rustpy.result import MultipleErrorsResult
from rustpy.result import Result


@dataclass(frozen=True)
class InstructionCall(Statement[PackageSemanticContext]):
    """Узел вызова инструкции"""

    id: Identifier
    """Идентификатор выражения"""
    args: Iterable[Expression]
    """Аргументы"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[InstructionCall, Iterable[str]]:
        """Парсинг инструкций"""
        ret = MultipleErrorsResult()

        _id = ret.putSingle(Identifier.parse(parser))
        args = ret.putMulti(parser.arguments(lambda: Expression.parse(parser), TokenType.Comma, TokenType.StatementEnd))

        return ret.make(lambda: cls(_id.unwrap(), args.unwrap()))
