from __future__ import annotations

from enum import StrEnum


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
