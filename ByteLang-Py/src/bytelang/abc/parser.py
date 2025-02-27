"""Парсер"""
from abc import ABC
from abc import abstractmethod
from typing import Iterable
from typing import Sequence

from bytelang.abc.Ast import Program
from bytelang.core.tokens import Token
from rustpy.result import Result


class Parser(ABC):
    """Парсер - создаёт AST"""

    @abstractmethod
    def run(self, tokens: Sequence[Token]) -> Result[Program, Iterable[str]]:
        """Создать AST"""
