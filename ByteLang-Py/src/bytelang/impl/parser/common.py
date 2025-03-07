from typing import Final
from typing import Iterable
from typing import Optional

from bytelang.abc.parser import Parsable
from bytelang.abc.parser import Parser
from bytelang.core.lexer import Lexer
from bytelang.core.stream import Stream
from bytelang.core.tokens import Token
from bytelang.core.tokens import TokenType
from bytelang.impl.node.directive import ConstDefine
from bytelang.impl.node.directive import Directive
from bytelang.impl.node.directive import MacroDefine
from bytelang.impl.node.directive import StructDefine
from bytelang.impl.node.statement import Statement
from bytelang.impl.registry.immediate import ImmediateRegistry
from rustpy.result import Result
from rustpy.result import SingleResult


class CommonParser(Parser[Statement]):
    """Общий парсер"""

    @classmethod
    def getDirectives(cls) -> Iterable[tuple[str, type[Parsable[Directive]]]]:
        """Получить директивы"""
        return (
            ("const", ConstDefine),
            ("struct", StructDefine),
            ("macro", MacroDefine)
        )

    def __init__(self, stream: Stream[Token]) -> None:
        super().__init__(stream)
        self.directive_registry: Final[ImmediateRegistry[str, type[Parsable[Directive]]]] = ImmediateRegistry(self.getDirectives())

    def _directive(self) -> Result[Directive, Iterable[str]]:
        """Парсинг директивы"""

        def _f(e):
            return (e,)

        if (identifier := self.consume(TokenType.Directive)).isError():
            return identifier.flow(_f)

        if (directive := self.directive_registry.get(identifier.unwrap().value)) is None:
            return SingleResult.error((f"Не удалось найти директиву: {identifier}",))

        node = directive.parse(self)

        if (token := self.consume(TokenType.StatementEnd)).isError():
            return token.flow(_f)

        return node

    def statement(self) -> Result[Optional[Statement], Iterable[str]]:
        if self.tokens.peek().type == TokenType.Directive:
            return self._directive()

        return super().statement()


def _test():
    from io import StringIO
    from bytelang.impl.node.program import Program
    from bytelang.core.stream import Stream
    from rustpy.exceptions import Panic

    code = """
    .struct MyStructType { byte: u8, int: i32 } 
    .macro foo(a, b, c) -> 12345 
    
    .const hola = @foo(1, 2, 3)
    """

    try:
        tokens = Lexer(TokenType.build_regex()).run(StringIO(code)).unwrap()
        print(tokens)
        print(Program.parse(CommonParser(Stream(tuple(tokens)))).unwrap())

    except Panic as e:
        print(e)

    return


if __name__ == '__main__':
    _test()
