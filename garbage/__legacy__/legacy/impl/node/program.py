from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from bytelang.legacy.abc.parser import Parser
from bytelang.legacy.abc.semantic import SemanticContext
from bytelang.legacy.core.result import LogResult
from bytelang.legacy.core.result import ResultAccumulator
from bytelang.legacy.impl.node.statement import Statement
from bytelang.legacy.impl.node.super import SuperNode


@dataclass(frozen=True)
class Program[S: SemanticContext](SuperNode[S, None, "Program"]):
    """Узел программы"""

    statements: Sequence[Statement]
    """Statements"""

    def accept(self, context: S) -> LogResult[None]:
        ret = ResultAccumulator()

        for statement in self.statements:
            ret.put(statement.accept(context))

        return ret.map(lambda _: None)

    @classmethod
    def parse(cls, parser: Parser) -> LogResult[Program]:
        ret = ResultAccumulator()

        while parser.tokens.peek() is not None:
            ret.put(parser.statement())

        return ret.map(lambda statements: Program(tuple(filter(None.__ne__, statements))))
