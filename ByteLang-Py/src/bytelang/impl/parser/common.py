from typing import Final
from typing import Iterable
from typing import Optional

from bytelang.abc.node import Directive
from bytelang.abc.node import Expression
from bytelang.abc.node import Statement
from bytelang.abc.parser import Parsable
from bytelang.abc.parser import Parser
from bytelang.core.tokens import TokenType
from bytelang.impl.node.common.directive import ConstDeclareDirective
from bytelang.impl.node.common.directive import MacroDeclareDirective
from bytelang.impl.node.common.directive import StructDeclareDirective
from bytelang.impl.node.common.expression import Identifier
from bytelang.impl.node.common.expression import Literal
from bytelang.impl.node.common.expression import Macro
from bytelang.impl.registry.immediate import ImmediateRegistry
from rustpy.result import Result


class CommonParser(Parser):
    """Общий парсер"""

    def __init__(self) -> None:
        self.directive_registry: Final[ImmediateRegistry[str, type[Parsable[Directive]]]] = ImmediateRegistry(self.getDirectives())

    @classmethod
    def getDirectives(cls) -> Iterable[tuple[str, type[Parsable[Directive]]]]:
        """Получить директивы"""
        return (
            ("const", ConstDeclareDirective),
            ("struct", StructDeclareDirective),
            ("macro", MacroDeclareDirective)
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
                return Result.error((f"Token not an expression: {not_expression_token}",))

    def _directive(self) -> Result[Directive, Iterable[str]]:
        """Парсинг директивы"""
        if (identifier := self.consume(TokenType.Directive)).isError():
            return Result.error(identifier.getError())

        if (directive := self.directive_registry.get(identifier.unwrap().value)) is None:
            return Result.error((f"Не удалось найти директиву: {identifier}",))

        return directive.parse(self)

    def statement(self) -> Result[Optional[Statement], Iterable[str]]:
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
