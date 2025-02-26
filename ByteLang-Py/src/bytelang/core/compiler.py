"""
Интерфейс компилятора
"""

from typing import BinaryIO
from typing import TextIO

from bytelang.abc.tokenizer import Tokenizer


class Compiler:
    """Компилятор"""

    tokenizer: Tokenizer

    def run(self, source: TextIO, bytecode: BinaryIO):
        """Преобразовать исходный код в байткод"""
        tokens = self.tokenizer.run(source)
        pass
