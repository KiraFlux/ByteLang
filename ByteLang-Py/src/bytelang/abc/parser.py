"""Парсер"""
from abc import ABC
from abc import abstractmethod
from typing import Iterable
from typing import Sequence

from bytelang.abc.node import Directive
from bytelang.abc.node import Expression
from bytelang.abc.node import Program
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
    def program(self) -> Result[Program, Iterable[str]]:
        """Парсинг узла программы"""

    @abstractmethod
    def expression(self) -> Result[Expression, Iterable[str]]:
        """Парсинг выражения"""

    @abstractmethod
    def directive(self) -> Result[Directive, Iterable[str]]:
        """Парсинг директивы"""

    @abstractmethod
    def arguments(self, delimiter: TokenType) -> Result[Sequence[Expression], Iterable[str]]:
        """Парсинг разделённых выражений"""
