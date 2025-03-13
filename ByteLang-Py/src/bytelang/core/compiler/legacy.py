"""
Интерфейс компилятора
"""
from dataclasses import dataclass
from typing import BinaryIO
from typing import Iterable
from typing import TextIO

from bytelang.abc.parser import Parser
from bytelang.core.lexer import Lexer
from bytelang.core.result import LogResult


@dataclass(frozen=True, kw_only=True)
class CompileInfo:
    """Сведения о компиляции программы"""

    compile_time: float
    """Время компиляции в секундах"""

    token_count: int
    """Количество токенов"""


class Compiler:
    """Компилятор"""

    lexer: Lexer
    parser: Parser

    def run(self, source: TextIO, bytecode: BinaryIO) -> LogResult[CompileInfo, Iterable[str]]:
        """Преобразовать исходный код в байткод"""
