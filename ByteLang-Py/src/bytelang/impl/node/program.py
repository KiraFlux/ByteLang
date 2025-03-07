from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from typing import Sequence

from bytelang.abc.parser import Parser
from bytelang.abc.semantic import SemanticContext
from bytelang.impl.node.statement import Statement
from bytelang.impl.node.super import SuperNode
from rustpy.result import Result
from rustpy.result import ResultAccumulator


@dataclass(frozen=True)
class Program[S: SemanticContext](SuperNode[S, None, "Program"]):
    """Узел программы"""

    statements: Sequence[Statement]
    """Statements"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Program, Iterable[str]]:
        resulter = ResultAccumulator()

        while parser.tokens.peek() is not None:
            node = parser.statement()

            if node.isOk() and node.unwrap() is not None:
                resulter.putMulti(node)

        return resulter.mapSingle(lambda statements: Program(statements))
