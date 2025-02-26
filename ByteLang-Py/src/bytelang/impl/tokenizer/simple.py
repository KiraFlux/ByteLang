import re
from typing import Iterable
from typing import Optional
from typing import TextIO

from bytelang.abc.tokenizer import Token
from bytelang.abc.tokenizer import TokenType
from bytelang.abc.tokenizer import Tokenizer


class SimpleTokenizer(Tokenizer):
    def __init__(self):
        self._token_regex = TokenType.build_regex()

    def run(self, source: TextIO) -> Iterable[Token]:
        """Разбивает исходный код на токены"""
        yield from (filter(None.__ne__, self._process(source.read())))

    def _process(self, source_read) -> Iterable[Optional[Token]]:
        for mo in re.finditer(self._token_regex, source_read):
            kind = mo.lastgroup
            yield TokenType[kind].transform(mo.group(kind))


def _test():
    from io import StringIO
    # Пример использования токенизатора
    code = """
            .const my_constant , 12345 + (32 - 3) * 6
            # комментарий
          instruction_invoke arg1, (arg3 + 4)



        """

    tokenizer = SimpleTokenizer()
    tokens = tokenizer.run(StringIO(code))

    for token in tokens:
        print(token)


if __name__ == "__main__":
    _test()
