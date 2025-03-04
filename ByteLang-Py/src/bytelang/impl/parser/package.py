"""Парсер файла пакета (Package)"""
from itertools import chain
from typing import Iterable

from bytelang.impl.node.common import ParsableDirective
from bytelang.impl.node.package import InstructionDeclareDirective
from bytelang.impl.parser.common import CommonParser


class PackageParser(CommonParser):

    @classmethod
    def getDirectives(cls) -> Iterable[tuple[str, type[ParsableDirective]]]:
        return chain(super().getDirectives(), (
            ("inst", InstructionDeclareDirective),
        ))


def _test():
    from bytelang.impl.lexer.simple import SimpleLexer

    lex = SimpleLexer()

    from io import StringIO
    tokens = lex.run(StringIO(".inst my_test_instruction(a: u32, b: i32)\n"))

    print(tokens)

    p = PackageParser()

    ast = p.run(tokens.unwrap())

    print(ast)


if __name__ == '__main__':
    _test()
