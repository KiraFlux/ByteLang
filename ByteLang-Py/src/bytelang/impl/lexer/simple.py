import re
from typing import Iterable
from typing import Sequence
from typing import TextIO

from bytelang.abc.lexer import Lexer
from bytelang.core.tokens import Token
from bytelang.core.tokens import TokenType
from rustpy.result import Result
from rustpy.result import ResultAccumulator
from rustpy.result import SingleResult


class SimpleLexer(Lexer):
    def __init__(self):
        self._token_regex = TokenType.build_regex()

    def run(self, source: TextIO) -> Result[Sequence[Token], Iterable[str]]:
        resulter = ResultAccumulator()

        for result in self._process(source.read()):
            resulter.putSingle(result)

        return resulter

    def _process(self, source_read: str) -> Iterable[Result[Token, str]]:
        position: int = 0

        while position < len(source_read):
            match = re.match(self._token_regex, source_read[position:])

            if match is None:
                yield SingleResult.error(f"Неизвестный символ: '{source_read[position]}' на позиции {position}")
                position += 1
                continue

            t = TokenType[match.lastgroup].transform(match.group())
            position += match.end()

            if t is None:
                continue

            yield SingleResult.ok(t)


def _test():
    from io import StringIO
    code_ok = """.this_is_directive "String1" "String2" 'c' 12345 123.456 identifier () {} [] <> + - * / = , : # comment"""
    code_error = "а 123456 о 123456 у 123456         ш             рз2нт !;№ 123456 "

    print("begin")

    lexer = SimpleLexer()
    result = lexer.run(StringIO(code_ok))

    if result.isError():
        print('\n'.join(result.getError()))
        return

    for token in result.unwrap():
        print(token)

    print("end")


if __name__ == "__main__":
    _test()
