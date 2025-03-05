"""Парсер файла пакета (Package)"""
from itertools import chain
from typing import Iterable

from bytelang.impl.node.common.directive import ParsableDirective
from bytelang.impl.node.package.directive import InstructionDeclareDirective
from bytelang.impl.parser.common import CommonParser


class PackageParser(CommonParser):

    @classmethod
    def getDirectives(cls) -> Iterable[tuple[str, type[ParsableDirective]]]:
        return chain(super().getDirectives(), (
            ("inst", InstructionDeclareDirective),
        ))


def _test():
    from bytelang.impl.lexer.simple import SimpleLexer
    from io import StringIO
    from rustpy.exceptions import Panic

    code = """
    
    .struct MyStruct { byte: u8, int: i32 }
    
    .inst MyInstruction(a: u8, context: MyStruct)
    
    .const MyConst = 12345
    
    """

    try:

        tokens = SimpleLexer().run(StringIO(code)).unwrap()
        print(tokens)
        print(PackageParser().run(tokens).unwrap())

    except Panic as e:
        print(e)

    return


if __name__ == '__main__':
    _test()
