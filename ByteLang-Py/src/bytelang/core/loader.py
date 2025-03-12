from dataclasses import dataclass
from typing import Callable
from typing import Iterable
from typing import TextIO

from bytelang.abc.semantic import SemanticContext
from bytelang.abc.stream import OutputStream
from bytelang.core.lexer import Lexer
from bytelang.core.result import Result
from bytelang.core.tokens import Token
from bytelang.impl.node.program import Program
from bytelang.impl.parser.common import CommonParser
from bytelang.impl.semantizer.common import CommonSemanticContext
from bytelang.impl.stream import CollectionOutputStream


@dataclass(frozen=True)
class Loader[T, S: SemanticContext]:
    """Загрузчик - преобразует исходный код в набор (Bundle)"""

    _lexer: Lexer
    _common_context: CommonSemanticContext
    _parser_maker: Callable[[OutputStream[Token]], CommonParser]
    _special_context_maker: Callable[[CommonSemanticContext], S]

    def load(self, source: TextIO) -> Result[T, Iterable[str]]:
        """Преобразовать исходный код в Bundle"""

        tokens = self._lexer.run(source)

        if tokens.isError():
            return tokens

        program = Program.parse(self._parser_maker(CollectionOutputStream(tuple(tokens.unwrap()))))

        if program.isError():
            return program

        special_context = self._special_context_maker(self._common_context)
        return program.unwrap().accept(special_context).map(lambda _: special_context.toBundle())
