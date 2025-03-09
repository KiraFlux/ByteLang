from dataclasses import dataclass

from bytelang.abc.profiles import MacroProfile
from bytelang.abc.profiles import RValueProfile
from bytelang.abc.profiles import TypeProfile
from bytelang.abc.registry import MutableRegistry
from bytelang.abc.semantic import SemanticContext


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
    from bytelang.impl.registry.immediate import MutableImmediateRegistry
    from rustpy.exceptions import Panic
    from bytelang.impl.serializer.primitive import u8
    from bytelang.impl.profiles.type import PrimitiveTypeProfile
    from bytelang.impl.node.program import Program
    from bytelang.impl.parser.common import CommonParser
    from bytelang.core.stream import OutputStream
    from bytelang.core.lexer import Lexer
    from bytelang.core.tokens import TokenType
    from io import StringIO

    code = """
    .struct MyStruct { foo: u8 }
    """

    def _pr(title: str, reg: MutableRegistry):
        print(f"{f" {title} ({len(tuple(reg.getItems()))}) ":-^40}")
        print("\n".join(map(str, reg.getItems())))

    try:

        tokens = Lexer(TokenType.build_regex()).run(StringIO(code)).unwrap()
        print(tokens)

        program = Program.parse(CommonParser(OutputStream(tuple(tokens)))).unwrap()
        print(program)

        context = CommonSemanticContext(
            macro_registry=MutableImmediateRegistry(()),
            type_registry=MutableImmediateRegistry((
                ("u8", PrimitiveTypeProfile(u8)),
            )),
            const_registry=MutableImmediateRegistry(()),
        )

        program.accept(context).unwrap()

        _pr("Constants", context.const_registry)
        _pr("Macro", context.macro_registry)
        _pr("Types", context.type_registry)

    except Panic as e:
        print(e)

    return


if __name__ == '__main__':
    _test()
