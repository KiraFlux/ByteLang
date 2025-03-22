"""Выражения, встречаемые только в source файле"""

from __future__ import annotations

from dataclasses import dataclass

from bytelang.abc.parser import Parser
from bytelang.core.result import LogResult
from bytelang.core.result import ResultAccumulator
from bytelang.core.tokens import TokenType
from bytelang.impl.node.component import HasUniqueArguments
from bytelang.impl.node.expression import Expression
from bytelang.impl.node.expression import HasExistingID
from bytelang.impl.node.expression import Identifier
from bytelang.impl.node.statement import Statement
from bytelang.impl.semantizer.sketch import SketchSemanticContext


@dataclass(frozen=True)
class InstructionCall(Statement[SketchSemanticContext], HasExistingID, HasUniqueArguments[Expression]):
    """Узел вызова инструкции"""

    def accept(self, context: SketchSemanticContext) -> LogResult[None]:
        ret = ResultAccumulator()
        pass  # TODO # TODO push to write stream (read / write streams)

        

        return ret.map(lambda _: None)

    @classmethod
    def parse(cls, parser: Parser) -> LogResult[InstructionCall]:
        """Парсинг инструкций"""
        ret = ResultAccumulator()

        _id = ret.put(Identifier.parse(parser))
        args = ret.put(parser.arguments(lambda: Expression.parse(parser), TokenType.Comma, TokenType.StatementEnd))

        return ret.map(lambda _: cls(args.unwrap(), _id.unwrap()))
