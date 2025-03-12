"""Парсер"""
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable
from typing import Iterable
from typing import Optional

from bytelang.abc.node import Node
from bytelang.abc.stream import OutputStream
from bytelang.core.tokens import Token
from bytelang.core.tokens import TokenType
from bytelang.core.LEGACY_result import MultiErrorLEGACYResult
from bytelang.core.LEGACY_result import LEGACY_Result
from bytelang.core.LEGACY_result import LEGACYResultAccumulator
from bytelang.core.LEGACY_result import SingleLEGACYResult


@dataclass
class Parser[Stmt: Node](ABC):
    """Парсер - создаёт AST"""

    tokens: OutputStream[Token]

    def consume(self, token_type: TokenType) -> LEGACY_Result[Token, str]:
        """Получить ожидаемый токен"""

        token = self.tokens.next()

        if token is None:
            return SingleLEGACYResult.error(f"Expect: {token_type}, got EOF")

        if token.type != token_type:
            return SingleLEGACYResult.error(f"Expect: {token_type}, got {token}")

        return SingleLEGACYResult.ok(token)

    def arguments[T: Node](
            self,
            element_parser: Callable[[], LEGACY_Result[T, Iterable[str]]],
            delimiter: TokenType,
            terminator: TokenType
    ) -> LEGACY_Result[Iterable[T], Iterable[str]]:
        """
        Разделенные элементы, заканчивающиеся токеном
        :param element_parser: Способ парсинга элемента
        :param delimiter: Разделитель элементов
        :param terminator: Токен окончания последовательности элементов
        :return:
        """

        if self.tokens.peek().type == terminator:
            self.tokens.next()
            return SingleLEGACYResult.ok(())

        resulter: LEGACYResultAccumulator[T, str] = LEGACYResultAccumulator()

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
            element_parser: Callable[[], LEGACY_Result[T, Iterable[str]]],
            brace_open: TokenType,
            brace_close: TokenType,
            delimiter: TokenType = TokenType.Comma
    ) -> LEGACY_Result[Iterable[T], Iterable[str]]:
        """
        Парсинг аргументов в скобках
        :param element_parser: Парсер элементов
        :param brace_open: открывающий токен
        :param brace_close: закрывающий токен
        :param delimiter: разделитель элементов
        :return: Последовательность узлов согласно функции парсера элементов
        """

        ret = MultiErrorLEGACYResult()

        ret.putSingle(self.consume(brace_open))
        args = ret.putMulti(self.arguments(element_parser, delimiter, brace_close))

        return ret.make(lambda: args.unwrap())

    def statement(self) -> LEGACY_Result[Optional[Stmt], Iterable[str]]:
        """Парсинг statement"""

        token = self.tokens.peek()
        self.tokens.next()

        if token.type == TokenType.StatementEnd:
            return SingleLEGACYResult.ok(None)

        return SingleLEGACYResult.error((f"Неуместный токен: {token}",))


class Parsable[T: Node]:
    """Способность парсинга узла"""

    @classmethod
    @abstractmethod
    def parse(cls, parser: Parser) -> LEGACY_Result[T, Iterable[str]]:
        """Парсинг узла с помощью парсера"""
