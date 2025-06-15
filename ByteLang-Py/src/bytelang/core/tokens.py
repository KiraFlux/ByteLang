from __future__ import annotations

import re
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from enum import auto
from re import Pattern
from typing import Callable
from typing import Sequence

from bytelang.core.key_word import Keyword
from bytelang.core.ops import Operator
from bytelang.legacy.abc.profiles import RValueProfile
from bytelang.legacy.impl.profiles.rvalue import FloatRV
from bytelang.legacy.impl.profiles.rvalue import IntegerRV
from rustpy.option import Option


class TokenKind(Enum):
    """Вид токена"""

    Skip = auto()
    Word = auto()
    Literal = auto()
    Operator = auto()
    Bracket = auto()
    Delimiter = auto()


@dataclass(frozen=True)
class _Spec[T](ABC):
    kind: TokenKind
    regex: str

    @abstractmethod
    def transform(self, lexeme: str) -> T:
        """Преобразовать лексему в значение"""


class _SpecWord(_Spec[str]):

    def transform(self, lexeme: str) -> str:
        return lexeme

    @classmethod
    def new(cls) -> _SpecWord:
        """Спецификация токена - слово"""
        return cls(TokenKind.Word, r'[a-zA-Z_]\w*')


class _SpecNone(_Spec[None]):
    def transform(self, lexeme: str) -> None:
        return None

    @classmethod
    def bracket(cls, c: str) -> _SpecNone:
        """Скобка"""
        return cls(TokenKind.Bracket, rf"\{c}")

    @classmethod
    def delimiter(cls, c: str) -> _SpecNone:
        """Разделитель"""
        return cls(TokenKind.Delimiter, c)

    @classmethod
    def skip(cls, c: str) -> _SpecNone:
        """Пропускаемый токен"""
        return cls(TokenKind.Skip, c)


@dataclass(frozen=True)
class _SpecOperator(_SpecNone):
    op: Operator

    @classmethod
    def new(cls, op: Operator) -> _SpecOperator:
        """Вид токена - оператор"""
        return cls(TokenKind.Operator, op.regex(), op)


@dataclass(frozen=True)
class _SpecLiteral[T](_Spec[T]):
    lexeme_transformer: Callable[[str], T]
    """Преобразователь лексемы в значение токена"""
    rvalue_maker: Callable[[T], RValueProfile]
    """Преобразователь значения токена в rvalue"""

    def transform(self, lexeme: str) -> T:
        return self.lexeme_transformer(lexeme)

    @classmethod
    def new(cls, pattern: str, transformer: Callable[[str], T], rv_maker: Callable[[T], RValueProfile]) -> _SpecLiteral[T]:
        """Создать вид литерала"""
        return cls(TokenKind.Literal, pattern, transformer, rv_maker)


class TokenType(Enum):
    """Тип токена"""

    # Литералы

    # string: _SpecLiteral[str] = _SpecLiteral.new(r'"([^"]*)"', lambda s: s.strip('"'), NotImplemented)
    character: _SpecLiteral[int] = _SpecLiteral.new(r"'.'", lambda c: ord(c.strip("'")), IntegerRV.new)
    real: _SpecLiteral[float] = _SpecLiteral.new(r'\d+\.\d+', float, FloatRV.new)
    integer: _SpecLiteral[int] = _SpecLiteral.new(r'\d+', int, IntegerRV.new)

    # Разделители

    comma = _SpecNone.delimiter(',')
    assign = _SpecNone.delimiter('=')
    colon = _SpecNone.delimiter(':')
    arrow = _SpecNone.delimiter('->')
    statementEnd = _SpecNone.delimiter(r'\n')

    # Операторы

    plus = _SpecOperator.new(Operator.Plus)
    """Оператор +"""
    minus = _SpecOperator.new(Operator.Minus)
    """Оператор -"""
    slash = _SpecOperator.new(Operator.Slash)
    """Оператор /"""
    star = _SpecOperator.new(Operator.Star)
    """Оператор *"""
    dot = _SpecOperator.new(Operator.Dot)
    """Оператор ."""

    # Скобки

    openRound = _SpecNone.bracket('(')
    """Открывающая круглая скобка"""
    closeRound = _SpecNone.bracket(')')
    """Закрывающая круглая скобка"""

    openFigure = _SpecNone.bracket('{')
    """Открывающая фигурная скобка"""
    closeFigure = _SpecNone.bracket('}')
    """Закрывающая фигурная скобка"""

    openSquare = _SpecNone.bracket('[')
    """Открывающая Квадратная скобка"""
    closeSquare = _SpecNone.bracket(']')
    """Закрывающая Квадратная скобка"""

    openAngle = _SpecNone.bracket('<')
    """Открывающая Угловая скобка"""
    closeAngle = _SpecNone.bracket('>')
    """Закрывающая Угловая скобка"""

    # Пропускающие

    comment = _SpecNone.skip(r'#.*')
    """Определение комментария"""
    skip = _SpecNone.skip(r'[ \t]+')
    """Символы пропуска"""

    # Слова

    keyword = _SpecWord(TokenKind.Word, NotImplemented)
    identifier = _SpecWord.new()

    @classmethod
    def build_regex(cls, keywords: Sequence[Keyword]) -> Pattern[str]:
        parts = list()

        parts.append(cls.keyword._makePattern(f'({"|".join(re.escape(kw.id) for kw in keywords)})'))

        parts.extend(
            fr'(?P<{token.name}>{token.value.regex})'
            for token in filter(
                lambda t: t not in (cls.keyword, cls.identifier),
                cls
            )
        )

        parts.append(cls.identifier._makePattern(cls.identifier.value.regex))

        join = '|'.join(parts)
        print(join)
        return re.compile(join)

    def _makePattern(self, regex: str) -> str:
        return fr'(?P<{self.name}>\b{regex}\b)'


@dataclass(frozen=True)
class Token[T]:
    """Токен"""

    type: TokenType
    """Тип токена"""
    lexeme: Option[T]
    """Лексема"""
