"""Парсер"""
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable
from typing import Iterable
from typing import Optional

from bytelang.legacy.abc.node import Node
from bytelang.legacy.core.result import ErrOne
from bytelang.legacy.core.result import LogResult
from bytelang.legacy.core.result import Ok
from bytelang.legacy.core.result import ResultAccumulator
from bytelang.legacy.core.stream import OutputStream
from bytelang.legacy.core.tokens import Token
from bytelang.legacy.core.tokens import TokenType


@dataclass
class Parser[Stmt: Node](ABC):
    """Парсер - создаёт AST"""

    tokens: OutputStream[Token]

    def consume(self, token_type: TokenType) -> LogResult[Token]:
        """Получить ожидаемый токен"""

        token = self.tokens.next()

        if token is None:
            return ErrOne(f"Expect: {token_type}, got EOF")

        if token.type != token_type:
            return ErrOne(f"Expect: {token_type}, got {token}")

        return Ok(token)

    def arguments[T: Node](
            self,
            element_parser: Callable[[], LogResult[T]],
            delimiter: TokenType,
            terminator: TokenType
    ) -> LogResult[Iterable[T]]:
        """
        Разделенные элементы, заканчивающиеся токеном
        :param element_parser: Способ парсинга элемента
        :param delimiter: Разделитель элементов
        :param terminator: Токен окончания последовательности элементов
        :return:
        """

        if self.tokens.peek().type == terminator:
            self.tokens.next()
            return Ok(())

        ret = ResultAccumulator()

        while True:
            ret.put(element_parser())

            token = self.tokens.next()

            if token is None:
                ret.put(ErrOne(f"Ожидался токен"))
                break

            if token.type == terminator:
                break

            if token.type != delimiter:
                ret.put(ErrOne(f"Expected '{delimiter}' between arguments"))
                break

        return ret.map()

    def braceArguments[T: Node](
            self,
            element_parser: Callable[[], LogResult[T]],
            brace_open: TokenType,
            brace_close: TokenType,
            delimiter: TokenType = TokenType.Comma
    ) -> LogResult[Iterable[T]]:
        """
        Парсинг аргументов в скобках
        :param element_parser: Парсер элементов
        :param brace_open: открывающий токен
        :param brace_close: закрывающий токен
        :param delimiter: разделитель элементов
        :return: Последовательность узлов согласно функции парсера элементов
        """

        ret = ResultAccumulator()

        ret.put(self.consume(brace_open))
        args = ret.put(self.arguments(element_parser, delimiter, brace_close))

        return ret.map(lambda _: args.unwrap())

    def statement(self) -> LogResult[Optional[Stmt]]:
        """Парсинг statement"""

        token = self.tokens.peek()
        self.tokens.next()

        if token.type == TokenType.StatementEnd:
            return Ok(None)

        return ErrOne(f"Неуместный токен: {token}")


class Parsable[T: Node]:
    """Способность парсинга узла"""

    @classmethod
    @abstractmethod
    def parse(cls, parser: Parser) -> LogResult[T]:
        """Парсинг узла с помощью парсера"""
