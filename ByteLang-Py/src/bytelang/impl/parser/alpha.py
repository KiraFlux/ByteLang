"""Альфа-реализация парсера"""
from typing import Iterable
from typing import Sequence

from bytelang.abc.node import Directive
from bytelang.abc.node import Expression
from bytelang.abc.node import Program
from bytelang.abc.node import Statement
from bytelang.abc.parser import Parser
from bytelang.core.tokens import Token
from bytelang.core.tokens import TokenType
from bytelang.impl.node.gamma import Identifier
from bytelang.impl.node.gamma import Instruction
from rustpy.result import Result


class AlphaParser(Parser):

    def expression(self) -> Result[Expression, Iterable[str]]:
        res = Identifier.parse(self.tokens)

        if res.isError():
            return Result.error((res.getError(),))

        return Result.ok(res.unwrap())

    def directive(self) -> Result[Directive, Iterable[str]]:
        pass

    def arguments(self, delimiter: TokenType) -> Result[Sequence[Expression], Iterable[str]]:
        args = list[Expression]()
        errors = list[str]()

        while self.tokens.peek().type != TokenType.StatementEnd:
            result = self.expression()

            if result.isError():
                errors.extend(result.getError())
            else:
                args.append(result.unwrap())

            token = self.tokens.next()

            if token.type == TokenType.StatementEnd:
                break

            if token.type != delimiter:
                errors.append(f"Expected '{delimiter}' between arguments")
                break

        self.tokens.next()

        return Result.error(errors) if errors else Result.ok(args)

    def program(self) -> Result[Program, Iterable[str]]:
        statements = list[Statement]()
        errors = list[str]()

        while (token := self.tokens.peek()) is not None:
            match token.type:
                case TokenType.StatementEnd:
                    self.tokens.next()
                    continue

                case TokenType.Identifier:
                    result = Instruction.parse(self)

                    if result.isError():
                        errors.extend(result.getError())
                    else:
                        statements.append(result.unwrap())

                case _:
                    errors.append(f"Неуместный токен: {token}")

        if errors:
            return Result.error(errors)

        return Result.ok(Program(statements))


def _test():
    tokens = (
        Token(TokenType.Star),
    )

    p = AlphaParser()
    print(p.run(tokens))


if __name__ == '__main__':
    _test()
