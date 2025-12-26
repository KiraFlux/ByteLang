from io import StringIO

from bytelang.core.key_word import Keyword
from bytelang.core.tokenizer import Tokenizer

k = (
    Keyword("struct", "Объявление структуры"),
    Keyword("macro", "Объявление макроса"),
    Keyword("const", "Объявление константы"),
    Keyword("inst", "Объявление сигнатуры инструкции"),
    Keyword("use", "Использование пакета инструкций"),
)

source = """

const a: [4]u8 = 123 as u8

use mypkg # использовать пакет mypkg

# Точка
struct Point<T> {
    x: T, # позиция X 
    y: T  # позиция Y
}

const p: Point<f32> = { 10.0, -50 + 50}

macro sq(x) -> x * x
"""

t = Tokenizer(k)

tokens = t.run(StringIO(source))

print(tokens)
