"""Парсер"""
from abc import ABC
from abc import abstractmethod
from typing import Callable
from typing import Iterable
from typing import Optional
from typing import Sequence

from bytelang.abc.node import Expression
from bytelang.abc.node import Node
from bytelang.abc.node import Program
from bytelang.abc.node import Statement
from bytelang.core.stream import Stream
from bytelang.core.tokens import Token
from bytelang.core.tokens import TokenType
from rustpy.result import Result


class Parser(ABC):
    """Парсер - создаёт AST"""

    tokens: Stream[Token]

    def run(self, tokens: Sequence[Token]) -> Result[Program, Iterable[str]]:
        """Создать AST"""
        self.tokens = Stream(tokens)
        return self.program()

    @abstractmethod
    def expression(self) -> Result[Expression, Iterable[str]]:
        """Парсинг выражения"""

    def consume(self, token_type: TokenType) -> Result[Token, str]:
        """Получить ожидаемый токен"""

        token = self.tokens.next()

        if token is None:
            return Result.error(f"Expect: {token_type}, got EOF")

        if token.type != token_type:
            return Result.error(f"Expect: {token_type}, got {token}")

        return Result.ok(token)

    def arguments[T: Node](
            self,
            element_parser: Callable[[], Result[T, Iterable[str]]],
            delimiter: TokenType,
            terminator: TokenType
    ) -> Result[Sequence[T], Iterable[str]]:
        """
        Разделенные элементы, заканчивающиеся токеном
        :param element_parser: Способ парсинга элемента
        :param delimiter: Разделитель элементов
        :param terminator: Токен окончания последовательности элементов
        :return:
        """
        if self.tokens.peek().type == terminator:
            return Result.ok(())

        items = list[T]()
        errors = list[str]()

        while True:
            result = element_parser()

            if result.isError():
                errors.extend(result.getError())
            else:
                items.append(result.unwrap())

            token = self.tokens.next()

            if token is None:
                errors.append(f"Ожидался токен")
                break

            if token.type == terminator:
                break

            if token.type != delimiter:
                errors.append(f"Expected '{delimiter}' between arguments")
                break

        return Result.chose(not errors, items, errors)

    def braceArguments[T: Node](
            self,
            element_parser: Callable[[], Result[T, Iterable[str]]],
            brace_open: TokenType,
            brace_close: TokenType,
            delimiter: TokenType = TokenType.Comma
    ) -> Result[Sequence[T], Iterable[str]]:
        """
        Парсинг аргументов в скобках
        :param element_parser: Парсер элементов
        :param brace_open: открывающий токен
        :param brace_close: закрывающий токен
        :param delimiter: разделитель элементов
        :return: Последовательность узлов согласно функции парсера элементов
        """

        if (begin := self.consume(brace_open)).isError():
            return Result.error((begin.getError(),))

        return self.arguments(element_parser, delimiter, brace_close)

    def statement(self) -> Result[Optional[Statement], Iterable[str]]:
        """Парсинг statement"""
        token = self.tokens.peek()
        self.tokens.next()

        if token.type == TokenType.StatementEnd:
            return Result.ok(None)

        return Result.error((f"Неуместный токен: {token}",))

    def program(self) -> Result[Program, Iterable[str]]:
        """Парсинг программы"""
        statements = list[Statement]()
        errors = list[str]()

        while self.tokens.peek() is not None:
            node = self.statement()

            if node.isOk():
                if (unwrap := node.unwrap()) is not None:
                    statements.append(unwrap)

            else:
                errors.extend(node.getError())

        return Result.chose(not errors, Program(statements), errors)


class Parsable[T: Node]:

    @classmethod
    @abstractmethod
    def parse(cls, parser: Parser) -> Result[T, Iterable[str]]:
        """Парсинг узла с помощью парсера"""
