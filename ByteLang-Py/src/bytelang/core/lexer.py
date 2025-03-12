import re
from dataclasses import dataclass
from typing import Iterable
from typing import TextIO

from bytelang.core.tokens import Token
from bytelang.core.tokens import TokenType
from bytelang.core.LEGACY_result import LEGACY_Result
from bytelang.core.LEGACY_result import LEGACYResultAccumulator
from bytelang.core.LEGACY_result import SingleLEGACYResult


@dataclass(frozen=True)
class Lexer:
    """Лексический анализатор - разбивает исходный код на токены"""

    _token_regex: str

    def run(self, source: TextIO) -> LEGACY_Result[Iterable[Token], Iterable[str]]:
        """
        Преобразовать исходный код в токены
        :param source: исходный код.
        :return Последовательность токенов
        """
        resulter = LEGACYResultAccumulator()

        for result in self._process(source.read()):
            resulter.putSingle(result)

        return resulter

    def _process(self, source_read: str) -> Iterable[LEGACY_Result[Token, str]]:
        position: int = 0

        while position < len(source_read):
            match = re.match(self._token_regex, source_read[position:])

            if match is None:
                yield SingleLEGACYResult.error(f"Неизвестный символ: '{source_read[position]}' на позиции {position}")
                position += 1
                continue

            t: Token = TokenType[match.lastgroup].transform(match.group())
            position += match.end()

            if t is None:
                continue

            yield SingleLEGACYResult.ok(t)


def _test():
    from io import StringIO
    code_ok = """.this_is_directive "String1" "String2" 'c' 12345 123.456 identifier () {} [] <> + - * / = , : # comment"""
    code_error = "а 123456 о 123456 у 123456         ш             рз2нт !;№ 123456 "

    print("begin")

    lexer = Lexer(TokenType.build_regex())
    result = lexer.run(StringIO(code_ok))

    if result.isError():
        print('\n'.join(result.getError()))
        return

    for token in result.unwrap():
        print(token)

    print("end")


if __name__ == "__main__":
    _test()
