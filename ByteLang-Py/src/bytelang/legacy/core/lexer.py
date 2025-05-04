from dataclasses import dataclass
from re import Match
from re import Pattern
from typing import Optional
from typing import TextIO

from bytelang.legacy.core.result import ErrOne
from bytelang.legacy.core.result import Ok
from bytelang.legacy.core.result import Result
from bytelang.legacy.core.result import ResultAccumulator
from bytelang.legacy.core.stream import CollectionOutputStream
from bytelang.legacy.core.stream import OutputStream
from bytelang.legacy.core.tokens import Token
from bytelang.legacy.core.tokens import TokenType

from bytelang.legacy.core.util.log import Logger

_log = Logger.fromFile(__file__)


class _LexerContext:
    """Контекст лексического анализатора"""

    def __init__(self, source: TextIO) -> None:
        self._source: str = source.read()
        self._position = 0

    def resolveToken(self, match: Optional[Match[str]]) -> Result[Optional[Token], OutputStream[str]]:
        """Определить токен"""
        if match is None:
            self._position += 1
            return ErrOne(f"Неизвестный символ: '{self._source[self._position]}' на позиции {self._position}")

        self._position += match.end()
        return Ok(TokenType[match.lastgroup].transform(match.group()))

    def isAvailable(self) -> bool:
        """Исходный код ещё не пуст"""
        return self._position < len(self._source)

    def getNextSubStr(self) -> str:
        """Получить срез строки исходного кода далее"""
        return self._source[self._position:]


@dataclass(frozen=True)
class Lexer:
    """Лексический анализатор - разбивает исходный код на токены"""

    _token_pattern: Pattern[str]

    # @_log.attach()
    def run(self, source: TextIO) -> Result[OutputStream[Token], OutputStream[str]]:
        """
        Преобразовать исходный код в токены
        :param source: исходный код.
        :return Последовательность токенов
        """
        context = _LexerContext(source)
        ret = ResultAccumulator()

        while context.isAvailable():
            ret.put(context.resolveToken(self._token_pattern.match(context.getNextSubStr())))

        return ret.map(lambda tokens: CollectionOutputStream(tuple(filter(lambda i: i is not None, tokens))))


def _test():
    from io import StringIO
    code_ok = """.this_is_directive "String1" "String2" 'c' 12345 123.456 identifier () {} [] <> + - * / = , : # comment"""
    code_error = "а 123456 о 123456 у 123456         ш             рз2нт !;№ 123456 "

    result = Lexer(TokenType.build_regex()).run(StringIO(code_ok))


if __name__ == "__main__":
    _test()
