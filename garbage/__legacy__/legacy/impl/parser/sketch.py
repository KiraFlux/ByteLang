"""Альфа-реализация парсера"""
from itertools import chain
from typing import Iterable
from typing import Optional

from bytelang.legacy.core.result import LogResult
from bytelang.legacy.core.tokens import TokenType
from bytelang.legacy.impl.node.directive.sketch import MarkDefine
from bytelang.legacy.impl.node.directive.sketch import SelectEnvironment
from bytelang.legacy.impl.node.directive.sketch import VarDefine
from bytelang.legacy.impl.node.directive.super import Directive
from bytelang.legacy.impl.node.instruction import InstructionCall
from bytelang.legacy.impl.node.statement import Statement
from bytelang.legacy.impl.parser.common import CommonParser


class SketchParser(CommonParser):
    """Парсер скетча"""

    @classmethod
    def getDirectives(cls) -> Iterable[type[Directive]]:
        return chain(super().getDirectives(), (SelectEnvironment, MarkDefine, VarDefine))

    def statement(self) -> LogResult[Optional[Statement], Iterable[str]]:
        if self.tokens.peek().type == TokenType.Identifier:
            return InstructionCall.parse(self)

        return super().statement()
