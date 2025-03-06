"""Семантический анализатор типов"""
from typing import Iterable

from bytelang.abc.node import Directive
from bytelang.abc.node import Program
from bytelang.abc.node import Statement
from bytelang.abc.semantizer import SemanticVisitor
from bytelang.impl.semantizer.context import CommonSemantizerContext
from rustpy.result import Result
from rustpy.result import ResultAccumulator
from rustpy.result import SingleResult


class TypeChecker(SemanticVisitor[CommonSemantizerContext]):
    """Семантический анализатор проверки типов"""

    def visit(self, node: Program, context: CommonSemantizerContext) -> Result[Program, Iterable[str]]:
        ret = ResultAccumulator()

        for statement in node.statements:
            ret.putMulti(self._visit_statement(statement, context))

        return ret.map(lambda s: Program(s))

    # TODO таблица вызовов на основании класса узла

    def _visit_statement(self, node: Statement, context: CommonSemantizerContext) -> Result[Statement, Iterable[str]]:
        if isinstance(node, Directive):
            pass

        return SingleResult.ok(node)
