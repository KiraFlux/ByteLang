from dataclasses import dataclass
from typing import Callable
from typing import TextIO

from bytelang.legacy.abc.semantic import SemanticContext
from bytelang.legacy.core.lexer import Lexer
from bytelang.legacy.core.result import LogResult
from bytelang.core.stream import OutputStream
from bytelang.legacy.core.tokens import Token
from bytelang.legacy.impl.node.program import Program
from bytelang.legacy.impl.parser.common import CommonParser
from bytelang.legacy.impl.semantizer.common import CommonSemanticContext


@dataclass(frozen=True)
class Loader[T, S: SemanticContext]:
    """Загрузчик - преобразует исходный код в набор (Bundle)"""

    _lexer: Lexer
    _common_context: CommonSemanticContext
    _parser_maker: Callable[[OutputStream[Token]], CommonParser]
    _special_context_maker: Callable[[CommonSemanticContext], S]

    def load(self, source: TextIO) -> LogResult[T]:
        """Преобразовать исходный код в Bundle"""
        return self._runLexer(source).andThen(self._runParser).andThen(self._runSemantizer)

    def _runLexer(self, source: TextIO) -> LogResult[OutputStream[Token]]:
        return self._lexer.run(source)

    def _runParser(self, tokens: OutputStream[Token]) -> LogResult[Program]:
        return Program.parse(self._parser_maker(tokens))

    def _runSemantizer(self, program: Program) -> LogResult[T]:
        context = self._special_context_maker(self._common_context)
        return program.accept(context).map(lambda _: context.toBundle())
