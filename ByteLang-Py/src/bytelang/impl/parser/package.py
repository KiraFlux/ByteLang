"""Парсер файла пакета (Package)"""
from itertools import chain
from typing import Iterable

from bytelang.abc.parser import Parsable
from bytelang.impl.node.directive import Directive
from bytelang.impl.node.directive import InstructionDefine
from bytelang.impl.parser.common import CommonParser


class PackageParser(CommonParser):

    @classmethod
    def getDirectives(cls) -> Iterable[tuple[str, type[Parsable[Directive]]]]:
        return chain(super().getDirectives(), (
            ("inst", InstructionDefine),
        ))
