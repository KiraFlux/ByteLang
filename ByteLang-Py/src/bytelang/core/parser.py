from bytelang.core.stream import OutputStream
from bytelang.core.tokens import Token


class Parser:
    """Парсер"""

    # Здесь нужна связь с тем, какие keywords доступны данному парсеру

    def run(self, tokens: OutputStream[Token]):  # TODO Result узел программы или stream ошибок (str)
        """Преобразование токенов в узел AST"""
