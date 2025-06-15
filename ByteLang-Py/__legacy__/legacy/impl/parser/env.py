from itertools import chain
from typing import Iterable

from bytelang.legacy.impl.node.directive.env import SetEnvDataPointer
from bytelang.legacy.impl.node.directive.env import SetEnvInstructionPointer
from bytelang.legacy.impl.node.directive.env import SetEnvProgramPointer
from bytelang.legacy.impl.node.directive.env import UsePackage
from bytelang.legacy.impl.node.directive.super import Directive
from bytelang.legacy.impl.parser.common import CommonParser


class EnvironmentParser(CommonParser):
    """Парсер окружения"""

    @classmethod
    def getDirectives(cls) -> Iterable[type[Directive]]:
        return chain(super().getDirectives(), (UsePackage, SetEnvDataPointer, SetEnvProgramPointer, SetEnvInstructionPointer))


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
    
    .ptr_prog u8
    .ptr_inst u16
    .ptr_data i32
    
    .use package{foo}
    .use packagege{bar, baz}
    .use pokopopo
    
    """

    from bytelang.legacy.impl.node.program import Program

    try:

        tokens = lexer.run(StringIO(code)).unwrap()
        parser = EnvironmentParser(tokens)

        ast = Program.parse(parser).unwrap()

        print(ast)

    except Panic as p:
        print(p)

    pass


if __name__ == '__main__':
    _test()
