"""Альфа-реализация парсера"""
from typing import Final
from typing import Iterable
from typing import Sequence

from bytelang.abc.node import Directive
from bytelang.abc.node import Expression
from bytelang.abc.node import Program
from bytelang.abc.node import Statement
from bytelang.abc.parser import Parser
from bytelang.core.tokens import Token
from bytelang.core.tokens import TokenType
from bytelang.impl.node.directives import EnvSelectDirective
from bytelang.impl.node.directives import ParsableDirective
from bytelang.impl.node.gamma import Identifier
from bytelang.impl.node.gamma import Instruction
from bytelang.impl.node.gamma import Literal
from bytelang.impl.registry.immediate import ImmediateRegistry
from rustpy.result import Result


class AlphaParser(Parser):
    directive_registry: Final[ImmediateRegistry[str, type[ParsableDirective]]] = ImmediateRegistry((
        ("env", EnvSelectDirective),
    ))

    def expression(self) -> Result[Expression, Iterable[str]]:
        match self.tokens.peek().type:
            case TokenType.Identifier:
                return Identifier.parse(self.tokens).map(lambda e: (e,))

            case literal_token if literal_token.isLiteral():
                return Literal.parse(self.tokens).map(lambda e: (e,))

            case not_expression_token:
                return Result.error((f"Token not an expression: {not_expression_token}",))

    def arguments(self, delimiter: TokenType) -> Result[Sequence[Expression], Iterable[str]]:
        if self.tokens.peek().type == TokenType.StatementEnd:
            return Result.ok(tuple())

        args = list[Expression]()
        errors = list[str]()

        while True:
            result = self.expression()

            if result.isError():
                errors.extend(result.getError())
            else:
                args.append(result.unwrap())

            token = self.tokens.next()

            if token is None:
                errors.append(f"Ожидался токен")
                break

            if token.type == TokenType.StatementEnd:
                break

            if token.type != delimiter:
                errors.append(f"Expected '{delimiter}' between arguments")
                break

        return Result.error(errors) if errors else Result.ok(args)

    def directive(self) -> Result[Directive, Iterable[str]]:
        if (identifier := self.tokens.next()) is None:
            return Result.error(("Ожидался токен",))

        if identifier.type != TokenType.Directive:
            return Result.error((f"Ожидалась директива, получено: {identifier}",))

        if (directive := self.directive_registry.get(identifier.value)) is None:
            return Result.error((f"Не удалось найти директиву: {identifier}",))

        return directive.parse(self)

    def program(self) -> Result[Program, Iterable[str]]:
        statements = list[Statement]()
        errors = list[str]()

        while (token := self.tokens.peek()) is not None:
            match token.type:
                case TokenType.StatementEnd:
                    self.tokens.next()

                case TokenType.Identifier:
                    result = Instruction.parse(self)

                    if result.isError():
                        errors.extend(result.getError())
                    else:
                        statements.append(result.unwrap())

                case TokenType.Directive:
                    result = self.directive()

                    if result.isError():
                        errors.extend(result.getError())
                    else:
                        statements.append(result.unwrap())

                case _:
                    errors.append(f"Неуместный токен: {token}")
                    self.tokens.next()

        if errors:
            return Result.error(errors)

        return Result.ok(Program(statements))


def _test():
    tokens = (
        Token(TokenType.Identifier, "MyInstruction"),
        Token(TokenType.Identifier, "x"),
        Token(TokenType.Comma), Token(TokenType.Integer, 1),
        Token(TokenType.Comma), Token(TokenType.String, "string"),
        Token(TokenType.StatementEnd),

        Token(TokenType.Identifier, "MyInstruction2"),
        Token(TokenType.Float, 123.456), Token(TokenType.Comma), Token(TokenType.Character, 0xFF),
        Token(TokenType.StatementEnd),

        Token(TokenType.Directive, "env"),
        Token(TokenType.Identifier, "esp32"),
        Token(TokenType.StatementEnd),

        # Token(TokenType.Directive, "i_am_not_exist"),
        Token(TokenType.StatementEnd),
    )

    p = AlphaParser()

    print(p.run(tokens))


if __name__ == '__main__':
    _test()
