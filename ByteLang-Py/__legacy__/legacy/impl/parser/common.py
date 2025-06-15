from __future__ import annotations

from typing import Final
from typing import Iterable
from typing import Optional

from bytelang.legacy.abc.parser import Parser
from bytelang.legacy.core.result import LogResult
from bytelang.core.stream import OutputStream
from bytelang.legacy.core.tokens import Token
from bytelang.legacy.core.tokens import TokenType
from bytelang.legacy.impl.node.directive.common import ConstDefine
from bytelang.legacy.impl.node.directive.common import MacroDefine
from bytelang.legacy.impl.node.directive.common import StructDefine
from bytelang.legacy.impl.node.directive.common import TypeAliasDefine
from bytelang.legacy.impl.node.directive.super import Directive
from bytelang.legacy.impl.node.statement import Statement
from bytelang.legacy.impl.registry.immediate import ImmediateRegistry


class CommonParser(Parser[Statement]):
    """Общий парсер"""

    @classmethod
    def getDirectives(cls) -> Iterable[type[Directive]]:
        """Получить директивы"""
        return (
            ConstDefine,
            StructDefine,
            MacroDefine,
            TypeAliasDefine
        )

    @classmethod
    def new(cls, tokens: OutputStream[Token]) -> CommonParser:
        """Создать новый экземпляр парсера"""
        return cls(tokens)

    def __init__(self, stream: OutputStream[Token]) -> None:
        super().__init__(stream)

        self.directive_registry: Final[ImmediateRegistry[str, type[Directive]]] = ImmediateRegistry((
            (d.getIdentifier(), d)
            for d in self.getDirectives()
        ))

    def _directive(self) -> LogResult[Directive]:
        """Парсинг директивы"""
        return (
            self.consume(TokenType.Directive)
            .andThen(lambda _id: self.directive_registry.get(_id.value))
            .andThen(lambda directive: directive.parse(self))
            .andThen(lambda node: self.consume(TokenType.StatementEnd).map(lambda _: node))
        )

    def statement(self) -> LogResult[Optional[Statement]]:
        if self.tokens.peek().type == TokenType.Directive:
            return self._directive()

        return super().statement()


def _test():
    from bytelang.legacy.core.lexer import Lexer
    from io import StringIO
    from rustpy.exceptions import Panic

    lexer = Lexer(TokenType.build_regex())

    code = """
    .macro abc() -> 1
    .const N = 1234
    .struct Point {x: f32, y: f32 }
    .const init_list = {1, 2, 3}
    """
    from bytelang.legacy.impl.node.program import Program

    try:

        tokens = lexer.run(StringIO(code)).unwrap()
        parser = CommonParser(tokens)

        ast = Program.parse(parser).unwrap()

        print(ast)

    except Panic as p:
        print(p)

    pass


if __name__ == '__main__':
    _test()
