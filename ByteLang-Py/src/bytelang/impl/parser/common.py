from typing import Final
from typing import Iterable
from typing import Optional

from bytelang.abc.parser import Parser
from bytelang.core.result import Result
from bytelang.core.result import SingleResult
from bytelang.core.stream import OutputStream
from bytelang.core.tokens import Token
from bytelang.core.tokens import TokenType
from bytelang.impl.node.directive.common import ConstDefine
from bytelang.impl.node.directive.common import MacroDefine
from bytelang.impl.node.directive.common import StructDefine
from bytelang.impl.node.directive.common import TypeAliasDefine
from bytelang.impl.node.directive.super import Directive
from bytelang.impl.node.statement import Statement
from bytelang.impl.registry.immediate import ImmediateRegistry


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

    def __init__(self, stream: OutputStream[Token]) -> None:
        super().__init__(stream)

        self.directive_registry: Final[ImmediateRegistry[str, type[Directive]]] = ImmediateRegistry((
            (d.getIdentifier(), d)
            for d in self.getDirectives()
        ))

    def _directive(self) -> Result[Directive, Iterable[str]]:
        """Парсинг директивы"""

        def _f(e):
            return (e,)

        if (identifier := self.consume(TokenType.Directive)).isError():
            return identifier.flow(_f)

        directive = self.directive_registry.get(identifier.unwrap().value)

        if directive.isError():
            return SingleResult.error((f"Не удалось найти директиву: {identifier}",))

        node = directive.unwrap().parse(self)

        if (token := self.consume(TokenType.StatementEnd)).isError():
            return token.flow(_f)

        return node

    def statement(self) -> Result[Optional[Statement], Iterable[str]]:
        if self.tokens.peek().type == TokenType.Directive:
            return self._directive()

        return super().statement()
