from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Callable
from typing import Final
from typing import Iterable
from typing import Optional
from typing import TextIO


class TokenType(Enum):
    String = r'"([^"]*)"', str
    Character = r"'([^']*)'", str
    Integer = r'\d+', int
    Float = r'\d+\.\d+', float
    Directive = r'\.[a-zA-Z_]\w*', lambda s: s.lstrip('.')
    Identifier = r'[a-zA-Z_]\w*', str
    Operator = r'[+\-*/]', str
    LeftPar = r'[(]'
    RightPar = r'[)]'
    Delimiter = r','
    StatementEnd = r'\n'
    Comment = r'#.*'
    Skip = r'[ \t]+'

    def __init__[T](self, pattern: str, transformer: Optional[Callable[[str], T]] = None) -> None:
        self.pattern: Final = pattern
        self._transformer: Final = transformer

    def transformLexeme(self, lexeme: str):
        """Преобразовать лексему в значение"""
        if self._transformer is None:
            return None

        return self._transformer(lexeme)

    def transform[T](self, lexeme: str) -> Optional[Token[T]]:
        """Создать токен на основе типа и лексемы"""
        if self._isSkipToken():
            return None

        return Token(self, self.transformLexeme(lexeme))

    def _isSkipToken(self) -> bool:
        return self in {self.Skip, self.Comment}

    @classmethod
    def build_regex(cls) -> str:
        """Создает регулярное выражение для токенизации"""
        return '|'.join(f'(?P<{token.name}>{token.pattern})' for token in cls)


@dataclass(frozen=True)
class Token[T: (int, str, float)]:
    """Токен (Единица языка) Имеет тип и лексему"""

    type: TokenType
    value: Optional[T]

    def __repr__(self) -> str:
        if self.value is None:
            return self.type.__str__()

        return f"{self.type}({self.value})"


class Tokenizer(ABC):
    """Tokenizer - разбивает исходный код на токены"""

    @abstractmethod
    def run(self, source: TextIO) -> Iterable[Token]:
        """
        :param source: исходный код
        :return Последовательность токенов
        """
        pass
