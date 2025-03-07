"""Альфа-реализация парсера"""
from itertools import chain
from typing import Iterable
from typing import Optional

from bytelang.abc.parser import Parsable
from bytelang.core.tokens import TokenType
from bytelang.impl.node.directive import Directive
from bytelang.impl.node.directive import EnvSelectDirective
from bytelang.impl.node.directive import MarkDefineDirective
from bytelang.impl.node.instruction import Instruction
from bytelang.impl.node.statement import Statement
from bytelang.impl.parser.common import CommonParser
from rustpy.result import Result


class SourceParser(CommonParser[Statement]):
    """Парсер исходного кода исполняемой программы"""

    @classmethod
    def getDirectives(cls) -> Iterable[tuple[str, type[Parsable[Directive]]]]:
        return chain(super().getDirectives(), (
            ("env", EnvSelectDirective),
            ("mark", MarkDefineDirective)
        ))

    def statement(self) -> Result[Optional[Statement], Iterable[str]]:
        if self.tokens.peek().type == TokenType.Identifier:
            return Instruction.parse(self)

        return super().statement()
