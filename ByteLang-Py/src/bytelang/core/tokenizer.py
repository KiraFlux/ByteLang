from typing import Sequence
from typing import TextIO

from bytelang.core.key_word import Keyword
from bytelang.core.stream import OutputStream
from bytelang.core.tokens import Token


class Tokenizer:
    """Лексический анализатор"""

    keywords: Sequence[Keyword]
    """Ключевые слова"""

    def run(self, source: TextIO) -> OutputStream[Token]:
        pass
