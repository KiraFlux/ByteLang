from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from typing import Sequence

from bytelang.abc.parser import Parser
from bytelang.abc.semantic import SemanticContext
from bytelang.core.result import MultipleErrorsResult
from bytelang.core.result import Result
from bytelang.core.result import ResultAccumulator
from bytelang.impl.node.statement import Statement
from bytelang.impl.node.super import SuperNode


@dataclass(frozen=True)
class Program[S: SemanticContext](SuperNode[S, None, "Program"]):
    """Узел программы"""

    statements: Sequence[Statement]
    """Statements"""

    def accept(self, context: S) -> Result[None, Iterable[str]]:
        ret = MultipleErrorsResult()

        for statement in self.statements:
            ret.putMulti(statement.accept(context))

        return ret.make(lambda: None)

    @classmethod
    def parse(cls, parser: Parser) -> Result[Program, Iterable[str]]:
        resulter = ResultAccumulator()

        while parser.tokens.peek() is not None:
            resulter.putMulti(parser.statement())

        return resulter.mapSingle(lambda statements: Program(tuple(filter(None.__ne__, statements))))
