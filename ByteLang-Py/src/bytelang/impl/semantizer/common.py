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
    from bytelang.impl.node.directive import ConstDefine
    from bytelang.impl.node.expression import Identifier
    from bytelang.impl.node.expression import BinaryOp, Literal
    from bytelang.core.ops import Operator
    from bytelang.core.profile.rvalue import IntegerRV
    from bytelang.impl.node.directive import MacroDefine
    from bytelang.impl.node.expression import MacroCall
    from bytelang.impl.registry.immediate import MutableImmediateRegistry

    # code = """
    # .const hola = 123
    # """

    try:

        # tokens = Lexer(TokenType.build_regex()).run(StringIO(code)).unwrap()
        # print(tokens)
        #
        # program = Program.parse(CommonParser(OutputStream(tuple(tokens)))).unwrap()
        # print(program)

        program = Program(
            statements=(

                MacroDefine(
                    arguments=(
                        Identifier("a"),
                        Identifier("b"),
                    ),
                    identifier=Identifier("add"),
                    template=BinaryOp(
                        op=Operator.Plus,
                        left=Identifier("a"),
                        right=Identifier("b")
                    )
                ),

                MacroDefine(
                    arguments=(
                        Identifier("a"),
                        Identifier("b"),
                    ),
                    identifier=Identifier("mul"),
                    template=BinaryOp(
                        op=Operator.Star,
                        left=Identifier("a"),
                        right=Identifier("b")
                    )
                ),

                ConstDefine(
                    identifier=Identifier("result"),
                    expression=MacroCall(
                        identifier=Identifier("mul"),
                        arguments=(
                            MacroCall(
                                identifier=Identifier("add"),
                                arguments=(
                                    Literal(IntegerRV.new(5)),
                                    Literal(IntegerRV.new(3)),
                                )
                            ),
                            MacroCall(
                                identifier=Identifier("add"),
                                arguments=(
                                    Literal(IntegerRV.new(1)),
                                    Literal(IntegerRV.new(7)),
                                )
                            ),
                        ),
                    )
                ),
            )
        )

        context = CommonSemanticContext(
            MutableImmediateRegistry(()),
            MutableImmediateRegistry(()),
            MutableImmediateRegistry(()),
        )

        program.accept(context).unwrap()

        print("\n".join(map(str, context.const_registry.getItems())))
        print("\n".join(map(str, context.macro_registry.getItems())))

    except Panic as e:
        print(e)

    return


if __name__ == '__main__':
    _test()
