from abc import ABC
from abc import abstractmethod
from typing import Iterable
from typing import Sequence
from typing import TextIO

from bytelang.core.tokens import Token
from rustpy.result import Result


class Lexer(ABC):
    """Лексический анализатор - разбивает исходный код на токены"""

    @abstractmethod
    def run(self, source: TextIO) -> Result[Sequence[Token], Iterable[str]]:
        """
        Преобразовать исходный код в токены
        :param source: исходный код.
        :return Последовательность токенов
        """
        pass
