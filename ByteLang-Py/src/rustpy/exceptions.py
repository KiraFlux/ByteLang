"""Исключения, эмулирующие панику"""


class RustPyException(Exception):
    """Основное исключение"""


class Panic(RustPyException):
    """Эмуляция паники"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
