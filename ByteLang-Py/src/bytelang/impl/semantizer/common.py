from dataclasses import dataclass

from bytelang.abc.registry import MutableRegistry
from bytelang.abc.semantic import SemanticContext
from bytelang.core.profile.macro import MacroProfile
from bytelang.core.profile.rvalue import RValueProfile
from bytelang.core.profile.type import TypeProfile


@dataclass
class CommonSemanticContext(SemanticContext):
    """Контекст общего назначения"""

    macro_registry: MutableRegistry[str, MacroProfile]
    """Реестр макросов"""

    type_registry: MutableRegistry[str, TypeProfile]
    """Реестр типов"""

    const_registry: MutableRegistry[str, RValueProfile]
    """Реестр констант"""


def _test():
    from rustpy.exceptions import Panic
    from bytelang.impl.node.program import Program
    from bytelang.impl.registry.immediate import MutableImmediateRegistry
    from bytelang.core.stream import OutputStream
    from bytelang.core.lexer import Lexer
    from bytelang.core.tokens import TokenType
    from io import StringIO
    from bytelang.impl.parser.common import CommonParser

    code = """
    .struct MyStruct { foo: *[123]**u8 } # Указатель на -> массив типа -> указатель на -> указатель на -> u8
    """

    try:

        tokens = Lexer(TokenType.build_regex()).run(StringIO(code)).unwrap()
        print(tokens)

        program = Program.parse(CommonParser(OutputStream(tuple(tokens)))).unwrap()
        print(program)

        context = CommonSemanticContext(
            MutableImmediateRegistry(()),
            MutableImmediateRegistry(()),
            MutableImmediateRegistry(()),
        )

        # program.accept(context).unwrap()

        print("\n".join(map(str, context.const_registry.getItems())))
        print("\n".join(map(str, context.macro_registry.getItems())))

    except Panic as e:
        print(e)

    return


if __name__ == '__main__':
    _test()
