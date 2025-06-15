from bytelang.core.key_word import Keyword
from bytelang.core.tokens import TokenType

k = (
    Keyword("struct", "Объявление структуры"),
    Keyword("macro", "Объявление макроса"),
    Keyword("const", "Объявление константы"),
    Keyword("inst", "Объявление сигнатуры инструкции"),
    Keyword("use", "Использование пакета инструкций"),
)

p = TokenType.build_regex(k)

print(p)
