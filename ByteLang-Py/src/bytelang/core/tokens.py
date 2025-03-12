from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from enum import auto
from re import Pattern
from typing import Callable
from typing import Optional

from bytelang.abc.profiles import RValueProfile
from bytelang.core.ops import Operator
from bytelang.impl.profiles.rvalue import FloatRV
from bytelang.impl.profiles.rvalue import IntegerRV

type _Value = str | int | float | None


class _Kind(Enum):
    """Вид токена"""

    Skip = auto()
    Common = auto()
    Literal = auto()
    Operator = auto()
    Bracket = auto()
    Delimiter = auto()


@dataclass(frozen=True)
class _Spec[T: _Value]:
    kind: _Kind
    pattern: str

    def transform(self, lexeme: str) -> T:
        """Преобразовать лексему в значение"""
        return None

    @classmethod
    def bracket(cls, c: str) -> _Spec[None]:
        """Скобка"""
        return cls(_Kind.Bracket, rf"\{c}")

    @classmethod
    def delimiter(cls, c: str) -> _Spec[None]:
        """Разделитель"""
        return cls(_Kind.Delimiter, c)

    @classmethod
    def skip(cls, c: str) -> _Spec[None]:
        """Пропуск"""
        return cls(_Kind.Skip, c)


@dataclass(frozen=True)
class _LexemeTransformer[T: _Value](_Spec):
    transformer: Optional[Callable[[str], T]]

    def transform(self, lexeme: str) -> T:
        if self.transformer is None:
            return None

        return self.transformer(lexeme)

    @classmethod
    def directive(cls) -> _Spec[str]:
        """Директива"""
        return cls(_Kind.Common, r'\.[a-zA-Z_]\w*', lambda s: s.lstrip('.'))

    @classmethod
    def macroCall(cls) -> _Spec[str]:
        """Вызов макроса"""
        return cls(_Kind.Common, r'\@[a-zA-Z_]\w*', lambda s: s.lstrip('@'))

    @classmethod
    def identifier(cls) -> _Spec[str]:
        """Идентификатор"""
        return cls(_Kind.Common, r'[a-zA-Z_]\w*', lambda s: s)


@dataclass(frozen=True)
class _LiteralSpec[T: (int, float, str)](_LexemeTransformer[T]):
    rvalue_maker: Callable[[T], RValueProfile]
    """Преобразователь токена в rvalue"""

    @classmethod
    def new(cls, pattern: str, transformer: Callable[[str], T], rv_maker: Callable[[T], RValueProfile]) -> _LiteralSpec[T]:
        """Создать вид литерала"""
        return cls(_Kind.Literal, pattern, transformer, rv_maker)


@dataclass(frozen=True)
class _SpecOp(_Spec[None]):
    op: Operator

    @classmethod
    def new(cls, op: Operator) -> _Spec[None]:
        """Вид токена - оператор"""
        return cls(_Kind.Operator, op.regex(), op)


class TokenType(Enum):
    """Тип токена"""

    # Директива

    Directive = _LexemeTransformer.directive()
    """Вызов директивы"""
    MacroCall = _LexemeTransformer.macroCall()
    """Вызов макроса"""
    Identifier = _LexemeTransformer.identifier()
    """Идентификатор (переменная, инструкция, константа, метка и т.п.)"""

    # Литералы

    String = _LiteralSpec.new(r'"([^"]*)"', lambda s: s.strip('"'), NotImplemented)
    """Строковый литерал"""
    Character = _LiteralSpec.new(r"'.'", lambda c: ord(c.strip("'")), IntegerRV.new)
    """Символьный литерал"""
    Float = _LiteralSpec.new(r'\d+\.\d+', float, FloatRV.new)
    """Вещественный литерал"""
    Integer = _LiteralSpec.new(r'\d+', int, IntegerRV.new)
    """Целочисленный литерал"""

    # Разделители

    Comma = _Spec.delimiter(',')
    """Разделитель аргументов"""
    Assignment = _Spec.delimiter('=')
    """Оператор = (Присваивание)"""
    Colon = _Spec.delimiter(':')
    """Разделитель идентификатора и типа"""
    Arrow = _Spec.delimiter('->')
    """Разделитель сигнатуры и возвращаемого значения"""
    StatementEnd = _Spec.delimiter(r'\n')
    """Окончание выражения"""

    # Операторы

    Plus = _SpecOp.new(Operator.Plus)
    """Оператор +"""
    Minus = _SpecOp.new(Operator.Minus)
    """Оператор -"""
    Slash = _SpecOp.new(Operator.Slash)
    """Оператор /"""
    Star = _SpecOp.new(Operator.Star)
    """Оператор *"""
    Dot = _SpecOp.new(Operator.Dot)
    """Оператор ."""

    # Скобки

    OpenRound = _Spec.bracket('(')
    """Открывающая круглая скобка"""
    CloseRound = _Spec.bracket(')')
    """Закрывающая круглая скобка"""

    OpenFigure = _Spec.bracket('{')
    """Открывающая фигурная скобка"""
    CloseFigure = _Spec.bracket('}')
    """Закрывающая фигурная скобка"""

    OpenSquare = _Spec.bracket('[')
    """Открывающая Квадратная скобка"""
    CloseSquare = _Spec.bracket(']')
    """Закрывающая Квадратная скобка"""

    OpenAngle = _Spec.bracket('<')
    """Открывающая Угловая скобка"""
    CloseAngle = _Spec.bracket('>')
    """Закрывающая Угловая скобка"""

    # Пропускающие

    Comment = _Spec.skip(r'#.*')
    """Определение комментария"""
    Skip = _Spec.skip(r'[ \t]+')
    """Символы пропуска"""

    def transform[T: _Value](self, lexeme: str) -> Optional[Token[T]]:
        """Создать токен на основе типа и лексемы"""
        if self.value.kind is _Kind.Skip:
            return None

        return Token(self, self.value.transform(lexeme))

    def _is(self, e: _Kind) -> bool:
        return self.value.kind == e

    def isLiteral(self) -> bool:
        """Токен является литералом"""
        return self._is(_Kind.Literal)

    def asOperator(self) -> Optional[Operator]:
        """Преобразовать токен в оператор"""
        if isinstance(self.value, _SpecOp):
            return self.value.op

    def getRightValueMaker[T](self) -> Optional[Callable[[Token[T]], RValueProfile]]:
        """Получить преобразователь из литерала в RV"""
        if isinstance(self.value, _LiteralSpec):
            return self.value.rvalue_maker

    @classmethod
    def build_regex(cls) -> Pattern[str]:
        """Создает регулярное выражение для лексического анализа"""
        return re.compile('|'.join(f'(?P<{token.name}>{token.value.pattern})' for token in cls))

    def __str__(self) -> str:
        return f"{self.__class__.__name__}<{self.name}>"


@dataclass(frozen=True)
class Token[T: _Value]:
    """Токен (Единица языка) Имеет тип и лексему"""

    type: TokenType
    value: T = None

    def __repr__(self) -> str:
        if self.value is None:
            return self.type.__str__()

        return f"{self.type}({self.value})"
