from dataclasses import dataclass

from bytelang.abc.profiles import PackageInstructionProfile
from bytelang.abc.registry import MutableRegistry
from bytelang.abc.semantic import SemanticContext
from bytelang.core.bundle.package import PackageBundle
from bytelang.impl.semantizer.common import CommonSemanticContext


@dataclass
class PackageSemanticContext(CommonSemanticContext, SemanticContext[PackageBundle]):
    """Семантический анализатор пакета"""

    instruction_registry: MutableRegistry[str, PackageInstructionProfile, str]
    """Реестр инструкций"""

    def toBundle(self) -> PackageBundle:
        return PackageBundle(
            instructions=self.instruction_registry
        )


def _test():
    from bytelang.impl.registry.immediate import MutableImmediateRegistry
    from rustpy.exceptions import Panic
    from bytelang.impl.serializer.primitive import u8
    from bytelang.impl.profiles.type import PrimitiveTypeProfile
    from bytelang.impl.node.program import Program
    from bytelang.core.stream import OutputStream
    from bytelang.core.lexer import Lexer
    from bytelang.core.tokens import TokenType
    from io import StringIO
    from bytelang.impl.parser.package import PackageParser

    code = """
    .inst MyInstruction(foo: u8, bar: *u8)
    .inst nop()
    """

    def _pr(title: str, reg: MutableRegistry):
        print(f"{f" {title} ({len(tuple(reg.getItems()))}) ":-^40}")
        print("\n".join(map(str, reg.getItems())))

    try:

        tokens = Lexer(TokenType.build_regex()).run(StringIO(code)).unwrap()
        print(tokens)

        program = Program.parse(PackageParser(OutputStream(tuple(tokens)))).unwrap()
        print(program)

        context = PackageSemanticContext(
            macro_registry=MutableImmediateRegistry(()),
            type_registry=MutableImmediateRegistry((
                ("u8", PrimitiveTypeProfile(u8)),
            )),
            const_registry=MutableImmediateRegistry(()),
            instruction_registry=MutableImmediateRegistry(())
        )

        program.accept(context).unwrap()

        _pr("Constants", context.const_registry)
        _pr("Macro", context.macro_registry)
        _pr("Types", context.type_registry)
        _pr("Instructions", context.instruction_registry)

    except Panic as e:
        print(e)

    return


if __name__ == '__main__':
    _test()
