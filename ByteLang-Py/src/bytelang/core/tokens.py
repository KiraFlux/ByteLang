from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import StrEnum
from enum import auto
from typing import Callable
from typing import Optional

type _Value = str | int | float | None


class Operator(StrEnum):
    """Операторы"""

    Dot = "."
    Plus = "+"
    Minus = "-"
    Star = "*"
    Slash = "/"

    def regex(self) -> str:
        """Преобразовать значение в регулярное выражение"""
        return rf"\{self.value}"


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
    def literal[T: _Value](cls, p: str, t: Callable[[str], T]) -> _Spec[T]:
        """Вид токена - литерал"""
        return cls(_Kind.Literal, p, t)

    @classmethod
    def directive(cls) -> _Spec[str]:
        """Директива"""
        return cls(_Kind.Common, r'\.[a-zA-Z_]\w*', lambda s: s.lstrip('.'))

    @classmethod
    def macro(cls) -> _Spec[str]:
        """Директива"""
        return cls(_Kind.Common, r'\@[a-zA-Z_]\w*', lambda s: s.lstrip('@'))


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

    Macro = _LexemeTransformer.macro()
    """Вызов макроса"""

    # Литералы

    String = _LexemeTransformer.literal(r'"([^"]*)"', lambda s: s.strip('"'))
    """Строковый литерал"""
    Character = _LexemeTransformer.literal(r"'.'", lambda c: ord(c.strip("'")))
    """Символьный литерал"""
    Float = _LexemeTransformer.literal(r'\d+\.\d+', float)
    """Вещественный литерал"""
    Integer = _LexemeTransformer.literal(r'\d+', int)
    """Целочисленный литерал"""
    Identifier = _LexemeTransformer.literal(r'[a-zA-Z_]\w*', lambda i: i)
    """Идентификатор (переменная, инструкция, константа, метка и т.п.)"""

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
        """Токен является оператором"""
        return self._is(_Kind.Literal)

    def asOperator(self) -> Optional[Operator]:
        """Преобразовать токен в оператор"""
        if isinstance(self.value, _SpecOp):
            return self.value.op

        return None

    @classmethod
    def build_regex(cls) -> str:
        """Создает регулярное выражение для лексического анализа"""
        return '|'.join(f'(?P<{token.name}>{token.value.pattern})' for token in cls)


@dataclass(frozen=True)
class Token[T: _Value]:
    """Токен (Единица языка) Имеет тип и лексему"""

    type: TokenType
    value: T = None

    def __repr__(self) -> str:
        if self.value is None:
            return self.type.__str__()

        return f"{self.type}({self.value})"
