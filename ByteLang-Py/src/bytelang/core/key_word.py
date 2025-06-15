from dataclasses import dataclass


@dataclass(frozen=True)
class Keyword:
    """Ключевое слово языка"""

    id: str
    """Идентификатор"""
    description: str
    """Описание"""
   