"""Парсер файла пакета (Package)"""
from itertools import chain
from typing import Iterable

from bytelang.impl.node.directive.super import Directive
from bytelang.impl.node.directive.package import InstructionDefine
from bytelang.impl.parser.common import CommonParser


class PackageParser(CommonParser):

    @classmethod
    def getDirectives(cls) -> Iterable[type[Directive]]:
        return chain(super().getDirectives(), (InstructionDefine,))
