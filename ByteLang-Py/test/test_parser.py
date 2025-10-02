from io import StringIO

from bytelang.core.key_word import Keyword
from bytelang.core.tokenizer import Tokenizer

k = (
    Keyword("struct", "Объявление структуры"),
)

source = """
# Точка
struct Point<T> {
    x: T, # позиция X 
    y: T  # позиция Y
}
"""

tokens = Tokenizer(k).run(StringIO(source))

print(tokens)
