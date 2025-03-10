from itertools import chain
from typing import Iterable

from bytelang.impl.node.directive.env import SetEnvDataPointer
from bytelang.impl.node.directive.env import SetEnvInstructionPointer
from bytelang.impl.node.directive.env import SetEnvProgramPointer
from bytelang.impl.node.directive.env import UsePackage
from bytelang.impl.node.directive.super import Directive
from bytelang.impl.parser.common import CommonParser


class EnvironmentParser(CommonParser):
    """Парсер окружения"""

    @classmethod
    def getDirectives(cls) -> Iterable[type[Directive]]:
        return chain(super().getDirectives(), (UsePackage, SetEnvDataPointer, SetEnvProgramPointer, SetEnvInstructionPointer))
