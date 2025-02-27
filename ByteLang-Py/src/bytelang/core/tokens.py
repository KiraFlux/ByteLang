from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import auto
from typing import Callable
from typing import Optional

type _Value = str | int | float | None


class _Hierarchy(Enum):
    """Модификация токена"""

    Stmt = auto()
    """
    Директивы, присваивания и другие инструкции.
    """

    Expr = auto()
    """
    Используется для представления всей структуры выражения, которое может быть вычислено или интерпретировано.
    """

    Term = auto()
    """
    Используется для группировки операций, которые имеют одинаковый приоритет, и для обработки более сложных выражений, состоящих из множества факторов.
    """

    Factor = auto()
    """
    Представляет собой базовые элементы выражения, такие как литералы, переменные, доступ к полям структур и выражения в скобках. 
    Это атомарные значения, которые могут быть использованы в более сложных выражениях.
    """


@dataclass(frozen=True)
class _Spec[T: _Value]:
    pattern: str
    transformer: Optional[Callable[[str], T]] = None
    hierarchy: Optional[_Hierarchy] = _Hierarchy.Factor

    def transformLexeme(self, lexeme: str) -> T:
        """Преобразовать лексему в значение"""
        if self.transformer is None:
            return None

        return self.transformer(lexeme)


class TokenType(Enum):
    """Тип токена"""

    # Литералы

    String = _Spec[str](r'"([^"]*)"', lambda s: s.strip('"'))
    """Строковый литерал"""
    Character = _Spec[int](r"'.'", lambda c: ord(c.strip("'")))
    """Символьный литерал"""
    Float = _Spec[float](r'\d+\.\d+', float)
    """Вещественный литерал"""
    Integer = _Spec[int](r'\d+', int)
    """Целочисленный литерал"""
    Identifier = _Spec[str](r'[a-zA-Z_]\w*', lambda i: i)
    """Идентификатор (переменная, инструкция, константа, метка и т.п.)"""

    # Директива

    Directive = _Spec[str](r'\.[a-zA-Z_]\w*', lambda s: s.lstrip('.'), hierarchy=_Hierarchy.Stmt)
    """Вызов директивы"""

    # Операторы

    Plus = _Spec[None](r'\+', hierarchy=_Hierarchy.Term)
    """Оператор +"""
    Minus = _Spec[None](r'-', hierarchy=_Hierarchy.Term)
    """Оператор -"""

    Slash = _Spec[None](r'/', hierarchy=_Hierarchy.Expr)
    """Оператор /"""
    Star = _Spec[None](r'\*', hierarchy=_Hierarchy.Expr)
    """Оператор *"""

    # Скобки

    OpenRound = _Spec[None](r'\(')
    """Открывающая круглая скобка"""
    CloseRound = _Spec[None](r'\)')
    """Закрывающая круглая скобка"""

    OpenFigure = _Spec[None](r'\{')
    """Открывающая фигурная скобка"""
    CloseFigure = _Spec[None](r'\}')
    """Закрывающая фигурная скобка"""

    OpenSquare = _Spec[None](r'\[')
    """Открывающая Квадратная скобка"""
    CloseSquare = _Spec[None](r'\]')
    """Закрывающая Квадратная скобка"""

    OpenAngle = _Spec[None](r'\<')
    """Открывающая Угловая скобка"""
    CloseAngle = _Spec[None](r'\>')
    """Закрывающая Угловая скобка"""

    # Разделители

    Assignment = _Spec[None](r'=', hierarchy=_Hierarchy.Stmt)
    """Оператор = (Присваивание)"""
    Delimiter = _Spec[None](r',', hierarchy=_Hierarchy.Stmt)
    """Разделитель аргументов"""
    Colon = _Spec[None](r':', hierarchy=_Hierarchy.Stmt)
    """Разделитель идентификатора и типа"""
    StatementEnd = _Spec[None](r'\n', hierarchy=_Hierarchy.Stmt)
    """Окончание выражения"""

    # Специальные

    Comment = _Spec(r'#.*', hierarchy=None)
    """Определение комментария"""
    Skip = _Spec(r'[ \t]+', hierarchy=None)
    """Символы пропуска"""

    def transform[T: _Value](self, lexeme: str) -> Optional[Token[T]]:
        """Создать токен на основе типа и лексемы"""
        if self.value.hierarchy is None:
            return None

        return Token(self, self.value.transformLexeme(lexeme))

    @classmethod
    def build_regex(cls) -> str:
        """Создает регулярное выражение для лексического анализа"""
        return '|'.join(f'(?P<{token.name}>{token.value.pattern})' for token in cls)


@dataclass(frozen=True)
class Token[T: _Value]:
    """Токен (Единица языка) Имеет тип и лексему"""

    type: TokenType
    value: T

    def __repr__(self) -> str:
        if self.value is None:
            return self.type.__str__()

        return f"{self.type}({self.value})"
