from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import auto

from rustpy.option import Option


class TokenType(Enum):
    """Тип токена"""

    # Литералы

    String = auto()
    Character = auto()
    Real = auto()
    Integer = auto()

    # Разделители

    Comma = auto()
    Assign = auto()
    Colon = auto()
    Arrow = auto()
    StatementEnd = auto()

    # Операторы

    Plus = auto()
    Dash = auto()
    Slash = auto()
    Star = auto()
    Dot = auto()
    Cast = auto()

    # Скобки

    OpenRound = auto()
    """Открывающая круглая скобка"""
    CloseRound = auto()
    """Закрывающая круглая скобка"""

    OpenFigure = auto()
    """Открывающая фигурная скобка"""
    CloseFigure = auto()
    """Закрывающая фигурная скобка"""

    OpenSquare = auto()
    """Открывающая Квадратная скобка"""
    CloseSquare = auto()
    """Закрывающая Квадратная скобка"""

    OpenAngle = auto()
    """Открывающая Угловая скобка"""
    CloseAngle = auto()
    """Закрывающая Угловая скобка"""

    # Пропускающие

    Comment = auto()
    """Определение комментария"""
    Skip = auto()
    """Символы пропуска"""

    # Слова

    Keyword = auto()
    """Ключевое слово"""
    Identifier = auto()
    """Идентификатор"""

    def __repr__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Token[T]:
    """Токен"""

    type: TokenType
    """Тип токена"""
    lexeme: Option[T]
    """Лексема"""
