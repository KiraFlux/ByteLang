"""Альфа-реализация парсера"""
from itertools import chain
from typing import Iterable
from typing import Optional

from bytelang.abc.node import Statement
from bytelang.core.tokens import TokenType
from bytelang.impl.node.common.directive import ParsableDirective
from bytelang.impl.node.source.directive import EnvSelectDirective
from bytelang.impl.node.source.statement import Instruction
from bytelang.impl.node.source.directive import MarkDeclareDirective
from bytelang.impl.parser.common import CommonParser
from rustpy.result import Result


class SourceParser(CommonParser):
    """Парсер исходного кода исполняемой программы"""

    @classmethod
    def getDirectives(cls) -> Iterable[tuple[str, type[ParsableDirective]]]:
        return chain(super().getDirectives(), (
            ("env", EnvSelectDirective),
            ("mark", MarkDeclareDirective)
        ))

    def statement(self) -> Result[Optional[Statement], Iterable[str]]:
        if self.tokens.peek().type == TokenType.Identifier:
            return Instruction.parse(self)

        return super().statement()


def _test():
    from bytelang.core.stream import Stream

    from bytelang.core.tokens import Token
    tokens = (
        # Token(TokenType.Identifier, "MyInstruction"),
        # Token(TokenType.Identifier, "x"),
        # Token(TokenType.Comma), Token(TokenType.Integer, 1),
        # Token(TokenType.Comma), Token(TokenType.String, "string"),
        # Token(TokenType.StatementEnd),
        #
        # Token(TokenType.Identifier, "MyInstruction2"),
        # Token(TokenType.Float, 123.456), Token(TokenType.Comma), Token(TokenType.Character, 0xFF),
        # Token(TokenType.StatementEnd),

        # Token(TokenType.Identifier, "my_var"),
        # Token(TokenType.Colon),
        # Token(TokenType.Identifier, "i32"),

        # Token(TokenType.Directive, "const"),
        # Token(TokenType.Identifier, "esp32"),
        # Token(TokenType.StatementEnd),
        #

        # Token(TokenType.Directive, "inst"),

        Token(TokenType.Identifier, "instruction"),
        Token(TokenType.OpenRound),

        Token(TokenType.Identifier, "x"),
        Token(TokenType.Colon),
        Token(TokenType.Identifier, "i32"),

        Token(TokenType.Comma),

        Token(TokenType.Identifier, "y"),
        Token(TokenType.Colon),
        Token(TokenType.Identifier, "u16"),

        Token(TokenType.CloseRound),

        Token(TokenType.StatementEnd),

    )

    # p = SourceParser()
    p = CommonParser()

    s = Stream(tokens)

    p.tokens = s

    from bytelang.impl.node.package.directive import InstructionDeclareDirective

    print(InstructionDeclareDirective.parse(p))

    # print(Field.parse(s))
    # print(p.run(tokens))
    # print("\n".join(map(str, p.directive_registry.getItems())))


if __name__ == '__main__':
    _test()
