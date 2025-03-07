"""
Интерфейс компилятора
"""
from dataclasses import dataclass
from time import time
from typing import BinaryIO
from typing import Iterable
from typing import TextIO

from bytelang.core.lexer import Lexer
from bytelang.abc.parser import Parser
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
    parser: Parser

    def run(self, source: TextIO, bytecode: BinaryIO) -> Result[CompileInfo, Iterable[str]]:
        """Преобразовать исходный код в байткод"""
        start_time = time()

        # Лексический анализ

        lexer_result = self.lexer.run(source)

        if lexer_result.isError():
            return Result.error(lexer_result.getError())

        tokens = lexer_result.unwrap()

        # Генерация AST

        parser_result = self.parser.run(tokens)

        if parser_result.isError():
            return Result.error(parser_result.getError())

        program = parser_result.unwrap()

        # Завершение работы

        return Result.ok(CompileInfo(
            compile_time=(time() - start_time),
            token_count=len(tokens)
        ))
