from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from typing import Sequence

from bytelang.abc.parser import Parser
from bytelang.abc.semantic import SemanticContext
from bytelang.core.LEGACY_result import MultiErrorLEGACYResult
from bytelang.core.LEGACY_result import LEGACY_Result
from bytelang.core.LEGACY_result import LEGACYResultAccumulator
from bytelang.impl.node.statement import Statement
from bytelang.impl.node.super import SuperNode


@dataclass(frozen=True)
class Program[S: SemanticContext](SuperNode[S, None, "Program"]):
    """Узел программы"""

    statements: Sequence[Statement]
    """Statements"""

    def accept(self, context: S) -> LEGACY_Result[None, Iterable[str]]:
        ret = MultiErrorLEGACYResult()

        for statement in self.statements:
            ret.putMulti(statement.accept(context))

        return ret.make(lambda: None)

    @classmethod
    def parse(cls, parser: Parser) -> LEGACY_Result[Program, Iterable[str]]:
        resulter = LEGACYResultAccumulator()

        while parser.tokens.peek() is not None:
            resulter.putMulti(parser.statement())

        return resulter.mapSingle(lambda statements: Program(tuple(filter(None.__ne__, statements))))
