"""
Интерфейс компилятора
"""
from dataclasses import dataclass
from time import time
from typing import BinaryIO
from typing import Iterable
from typing import TextIO

from bytelang.abc.lexer import Lexer
from rustpy.result import Result


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

    def run(self, source: TextIO, bytecode: BinaryIO) -> Result[CompileInfo, Iterable[str]]:
        """Преобразовать исходный код в байткод"""
        start_time = time()

        # Лексический анализ

        lexer_result = self.lexer.run(source)

        if lexer_result.isError():
            return Result.error(lexer_result.getError())

        tokens = lexer_result.unwrap()

        # Лексический анализ

        # Завершение работы

        return Result.ok(CompileInfo(
            compile_time=(time() - start_time),
            token_count=len(tokens)
        ))
