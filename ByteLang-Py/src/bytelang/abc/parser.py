"""Парсер"""
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable
from typing import Iterable
from typing import Optional

from bytelang.abc.node import Node
from bytelang.core.stream import OutputStream
from bytelang.core.tokens import Token
from bytelang.core.tokens import TokenType
from bytelang.core.result import MultiErrorResult
from bytelang.core.result import Result
from bytelang.core.result import ResultAccumulator
from bytelang.core.result import SingleResult


@dataclass
class Parser[Stmt: Node](ABC):
    """Парсер - создаёт AST"""

    tokens: OutputStream[Token]

    def consume(self, token_type: TokenType) -> Result[Token, str]:
        """Получить ожидаемый токен"""

        token = self.tokens.next()

        if token is None:
            return SingleResult.error(f"Expect: {token_type}, got EOF")

        if token.type != token_type:
            return SingleResult.error(f"Expect: {token_type}, got {token}")

        return SingleResult.ok(token)

    def arguments[T: Node](
            self,
            element_parser: Callable[[], Result[T, Iterable[str]]],
            delimiter: TokenType,
            terminator: TokenType
    ) -> Result[Iterable[T], Iterable[str]]:
        """
        Разделенные элементы, заканчивающиеся токеном
        :param element_parser: Способ парсинга элемента
        :param delimiter: Разделитель элементов
        :param terminator: Токен окончания последовательности элементов
        :return:
        """

        if self.tokens.peek().type == terminator:
            self.tokens.next()
            return SingleResult.ok(())

        resulter: ResultAccumulator[T, str] = ResultAccumulator()

        while True:
            resulter.putMulti(element_parser())

            token = self.tokens.next()

            if token is None:
                resulter.putOptionalError(f"Ожидался токен")
                break

            if token.type == terminator:
                break

            if token.type != delimiter:
                resulter.putOptionalError(f"Expected '{delimiter}' between arguments")
                break

        return resulter

    def braceArguments[T: Node](
            self,
            element_parser: Callable[[], Result[T, Iterable[str]]],
            brace_open: TokenType,
            brace_close: TokenType,
            delimiter: TokenType = TokenType.Comma
    ) -> Result[Iterable[T], Iterable[str]]:
        """
        Парсинг аргументов в скобках
        :param element_parser: Парсер элементов
        :param brace_open: открывающий токен
        :param brace_close: закрывающий токен
        :param delimiter: разделитель элементов
        :return: Последовательность узлов согласно функции парсера элементов
        """

        ret = MultiErrorResult()

        ret.putSingle(self.consume(brace_open))
        args = ret.putMulti(self.arguments(element_parser, delimiter, brace_close))

        return ret.make(lambda: args.unwrap())

    def statement(self) -> Result[Optional[Stmt], Iterable[str]]:
        """Парсинг statement"""

        token = self.tokens.peek()
        self.tokens.next()

        if token.type == TokenType.StatementEnd:
            return SingleResult.ok(None)

        return SingleResult.error((f"Неуместный токен: {token}",))


class Parsable[T: Node]:
    """Способность парсинга узла"""

    @classmethod
    @abstractmethod
    def parse(cls, parser: Parser) -> Result[T, Iterable[str]]:
        """Парсинг узла с помощью парсера"""
