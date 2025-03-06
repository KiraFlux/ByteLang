from typing import Final
from typing import Iterable
from typing import Optional

from bytelang.abc.node import Directive
from bytelang.abc.node import Expression
from bytelang.abc.node import Statement
from bytelang.abc.parser import Parsable
from bytelang.abc.parser import Parser
from bytelang.core.tokens import TokenType
from bytelang.impl.node.directive import ConstDefineDirective
from bytelang.impl.node.directive import MacroDefineDirective
from bytelang.impl.node.directive import StructDefineDirective
from bytelang.impl.node.expression import Identifier
from bytelang.impl.node.expression import Literal
from bytelang.impl.node.expression import Macro
from bytelang.impl.registry.immediate import ImmediateRegistry
from rustpy.result import Result
from rustpy.result import SingleResult


class CommonParser(Parser):
    """Общий парсер"""

    def __init__(self) -> None:
        self.directive_registry: Final[ImmediateRegistry[str, type[Parsable[Directive]]]] = ImmediateRegistry(self.getDirectives())

    @classmethod
    def getDirectives(cls) -> Iterable[tuple[str, type[Parsable[Directive]]]]:
        """Получить директивы"""
        return (
            ("const", ConstDefineDirective),
            ("struct", StructDefineDirective),
            ("macro", MacroDefineDirective)
        )

    def expression(self) -> Result[Expression, Iterable[str]]:
        match self.tokens.peek().type:
            case TokenType.Identifier:
                return Identifier.parse(self)

            case TokenType.Macro:
                return Macro.parse(self)

            case literal_token if literal_token.isLiteral():
                return Literal.parse(self)

            case not_expression_token:
                return SingleResult.error((f"Token not an expression: {not_expression_token}",))

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

    def statement(self) -> Optional[Result[Statement, Iterable[str]]]:
        if self.tokens.peek().type == TokenType.Directive:
            return self._directive()

        return super().statement()


def _test():
    from bytelang.impl.lexer.simple import SimpleLexer
    from rustpy.exceptions import Panic
    from io import StringIO

    code = """
    .struct MyStructType { byte: u8, int: i32 } 
    .macro foo(a, b, c) -> 12345 
    
    .const hola = @foo(1, 2, 3)
    """

    try:
        tokens = SimpleLexer().run(StringIO(code)).unwrap()
        print(tokens)
        print(CommonParser().run(tokens).unwrap())

    except Panic as e:
        print(e)

    return


if __name__ == '__main__':
    _test()
