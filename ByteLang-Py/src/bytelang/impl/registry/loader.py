from pathlib import Path
from typing import Callable
from typing import Iterable
from typing import TextIO

from bytelang.abc.registry import CatalogRegistry
from bytelang.abc.semantic import SemanticContext
from bytelang.core.lexer import Lexer
from bytelang.core.result import Result
from bytelang.core.result import SingleResult
from bytelang.core.stream import OutputStream
from bytelang.core.tokens import Token
from bytelang.core.tokens import TokenType
from bytelang.impl.node.program import Program
from bytelang.impl.parser.common import CommonParser
from bytelang.impl.semantizer.common import CommonSemanticContext


class CodeLoadingRegistry[Bnd, S: SemanticContext](CatalogRegistry[Bnd, Iterable[str]]):
    """Реестр загрузки кода"""

    def __init__(
            self,
            catalog: Path,
            common_context: CommonSemanticContext,
            parser_maker: Callable[[OutputStream[Token]], CommonParser],
            special_context_maker: Callable[[CommonSemanticContext], S]
    ) -> None:
        super().__init__(catalog, "bls")
        self._common_context = common_context
        self._parser_maker = parser_maker
        self._special_context_maker = special_context_maker

    def _loadFile(self, filepath: Path) -> Result[Bnd, Iterable[str]]:
        try:
            with open(filepath) as source:
                return self._processSource(source)

        except OSError as e:
            return SingleResult.error(f"Cannot open {filepath}: {e}")

    def _processSource(self, source: TextIO) -> Result[Bnd, Iterable[str]]:
        tokens = Lexer(TokenType.build_regex()).run(source)

        if tokens.isError():
            return tokens

        program = Program.parse(self._parser_maker(OutputStream(tuple(tokens.unwrap()))))

        if program.isError():
            return program

        special_context = self._special_context_maker(self._common_context)
        ret = program.unwrap().accept(special_context)

        return ret.map(lambda _: special_context.toBundle())
