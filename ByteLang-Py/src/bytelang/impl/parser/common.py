from typing import Final
from typing import Iterable
from typing import Optional

from bytelang.abc.node import Directive
from bytelang.abc.node import Expression
from bytelang.abc.node import Statement
from bytelang.abc.parser import Parser
from bytelang.core.tokens import TokenType
from bytelang.impl.node.common import ConstDeclareDirective
from bytelang.impl.node.common import Identifier
from bytelang.impl.node.common import Literal
from bytelang.impl.node.common import ParsableDirective
from bytelang.impl.registry.immediate import ImmediateRegistry
from rustpy.result import Result


class CommonParser(Parser):
    """Общий парсер"""

    def __init__(self) -> None:
        self.directive_registry: Final[ImmediateRegistry[str, type[ParsableDirective]]] = ImmediateRegistry(self.getDirectives())

    @classmethod
    def getDirectives(cls) -> Iterable[tuple[str, type[ParsableDirective]]]:
        """Получить директивы"""
        return (
            ("const", ConstDeclareDirective),
        )

    def expression(self) -> Result[Expression, Iterable[str]]:
        match self.tokens.peek().type:
            case TokenType.Identifier:
                return Identifier.parse(self.tokens).map(lambda e: (e,))

            case literal_token if literal_token.isLiteral():
                return Literal.parse(self.tokens).map(lambda e: (e,))

            case not_expression_token:
                return Result.error((f"Token not an expression: {not_expression_token}",))

    def _directive(self) -> Result[Directive, Iterable[str]]:
        """Парсинг директивы"""

        if (identifier := self.tokens.next()) is None:
            return Result.error(("Ожидался токен",))

        if identifier.type != TokenType.Directive:
            return Result.error((f"Ожидалась директива, получено: {identifier}",))

        if (directive := self.directive_registry.get(identifier.value)) is None:
            return Result.error((f"Не удалось найти директиву: {identifier}",))

        return directive.parse(self)

    def statement(self) -> Result[Optional[Statement], Iterable[str]]:
        if self.tokens.peek().type == TokenType.Directive:
            return self._directive()

        return super().statement()
