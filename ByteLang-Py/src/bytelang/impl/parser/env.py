from itertools import chain
from typing import Iterable

from bytelang.impl.node.directive import Directive
from bytelang.impl.node.directive import UsePackage
from bytelang.impl.parser.common import CommonParser


class EnvironmentParser(CommonParser):
    """Парсер окружения"""

    @classmethod
    def getDirectives(cls) -> Iterable[type[Directive]]:
        return chain(super().getDirectives(), (UsePackage,))
