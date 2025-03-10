"""Выражения, встречаемые только в source файле"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from bytelang.abc.parser import Parser
from bytelang.core.result import MultiErrorResult
from bytelang.core.result import Result
from bytelang.core.tokens import TokenType
from bytelang.impl.node.expression import Expression
from bytelang.impl.node.expression import Identifier
from bytelang.impl.node.statement import Statement
from bytelang.impl.node.component import HasUniqueArguments
from bytelang.impl.node.expression import HasExistingID
from bytelang.impl.semantizer.source import SketchSemanticContext


@dataclass(frozen=True)
class InstructionCall(Statement[SketchSemanticContext], HasExistingID, HasUniqueArguments[Expression]):
    """Узел вызова инструкции"""

    def accept(self, context: SketchSemanticContext) -> Result[None, Iterable[str]]:
        ret = MultiErrorResult()
        pass  # TODO # TODO push to write stream (read / write streams)

        # ret.putOptionalError(self.checkIdentifier())

        return ret.make(lambda: None)

    @classmethod
    def parse(cls, parser: Parser) -> Result[InstructionCall, Iterable[str]]:
        """Парсинг инструкций"""
        ret = MultiErrorResult()

        _id = ret.putSingle(Identifier.parse(parser))
        args = ret.putMulti(parser.arguments(lambda: Expression.parse(parser), TokenType.Comma, TokenType.StatementEnd))

        return ret.make(lambda: cls(args.unwrap(), _id.unwrap()))
