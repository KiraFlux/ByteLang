"""Alpha Parser"""

from typing import Iterable
from typing import Sequence

from bytelang.abc.Ast import Program
from bytelang.abc.parser import Parser
from bytelang.core.tokens import Token
from rustpy.result import Result


class AlphaParser(Parser):
    def run(self, tokens: Sequence[Token]) -> Result[Program, Iterable[str]]:
        pass
