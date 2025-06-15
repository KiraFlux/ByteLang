"""Парсер файла пакета (Package)"""
from itertools import chain
from typing import Iterable

from bytelang.legacy.impl.node.directive.package import InstructionDefine
from bytelang.legacy.impl.node.directive.super import Directive
from bytelang.legacy.impl.parser.common import CommonParser


class PackageParser(CommonParser):

    @classmethod
    def getDirectives(cls) -> Iterable[type[Directive]]:
        return chain(super().getDirectives(), (InstructionDefine,))


def _test():
    from bytelang.legacy.core.lexer import Lexer
    from io import StringIO
    from rustpy.exceptions import Panic

    from bytelang.legacy.core.tokens import TokenType
    lexer = Lexer(TokenType.build_regex())

    code = """
    
    .macro abc() -> 1
    .const N = 1234
    .struct Point {x: f32, y: f32 }
    .inst foo(a: int, b: [10]u8)
    
    """
    from bytelang.legacy.impl.node.program import Program

    try:

        tokens = lexer.run(StringIO(code)).unwrap()
        parser = PackageParser(tokens)

        ast = Program.parse(parser).unwrap()

        print(ast)

    except Panic as p:
        print(p)

    pass


if __name__ == '__main__':
    _test()
