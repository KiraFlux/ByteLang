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
from rustpy.result import MultipleErrorsResult
from rustpy.result import Result
from rustpy.result import ResultAccumulator
from rustpy.result import SingleResult


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
            return SingleResult.ok(())

        resulter: ResultAccumulator[T, str] = ResultAccumulator()

        while True:
            resulter.putMulti(element_parser())

            token = self.tokens.next()

            if token is None:
                resulter.putError(f"Ожидался токен")
                break

            if token.type == terminator:
                break

            if token.type != delimiter:
                resulter.putError(f"Expected '{delimiter}' between arguments")
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
        ret = MultipleErrorsResult()
        ret.putSingle(self.consume(brace_open))
        args = ret.putMulti(self.arguments(element_parser, delimiter, brace_close))
        return ret.make(lambda: args.unwrap())

    def statement(self) -> Optional[Result[Statement, Iterable[str]]]:
        """Парсинг statement"""
        token = self.tokens.peek()
        self.tokens.next()

        if token.type == TokenType.StatementEnd:
            return None

        return SingleResult.error((f"Неуместный токен: {token}",))

    def program(self) -> Result[Program, Iterable[str]]:
        """Парсинг программы"""
        resulter = ResultAccumulator()

        while self.tokens.peek() is not None:
            node = self.statement()

            if node is not None:
                resulter.putMulti(node)

        return resulter.mapSingle(lambda statements: Program(statements))


class Parsable[T: Node]:
    """Способность парсинга узла"""

    @classmethod
    @abstractmethod
    def parse(cls, parser: Parser) -> Result[T, Iterable[str]]:
        """Парсинг узла с помощью парсера"""
