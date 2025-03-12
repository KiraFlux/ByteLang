"""Альфа-реализация парсера"""
from itertools import chain
from typing import Iterable
from typing import Optional

from bytelang.core.result import Result
from bytelang.core.tokens import TokenType
from bytelang.impl.node.directive.sketch import MarkDefine
from bytelang.impl.node.directive.sketch import SelectEnvironment
from bytelang.impl.node.directive.super import Directive
from bytelang.impl.node.instruction import InstructionCall
from bytelang.impl.node.statement import Statement
from bytelang.impl.parser.common import CommonParser


class SketchParser(CommonParser):
    """Парсер скетча"""

    @classmethod
    def getDirectives(cls) -> Iterable[type[Directive]]:
        return chain(super().getDirectives(), (SelectEnvironment, MarkDefine))

    def statement(self) -> Result[Optional[Statement], Iterable[str]]:
        if self.tokens.peek().type == TokenType.Identifier:
            return InstructionCall.parse(self)

        return super().statement()
