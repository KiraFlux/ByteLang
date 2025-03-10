from dataclasses import dataclass

from bytelang.abc.registry import MutableRegistry
from bytelang.core.bundle.env import EnvironmentBundle
from bytelang.core.bundle.package import PackageBundle
from bytelang.impl.semantizer.common import CommonSemanticContext


@dataclass(frozen=True)
class EnvironmentSemanticContext(CommonSemanticContext[EnvironmentBundle]):
    """Контекст семантического анализа файла окружения"""

    package_registry: MutableRegistry[str, PackageBundle]
    """Реестр пакетов"""

    def toBundle(self) -> EnvironmentBundle:
        pass


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
    from bytelang.impl.parser.common import CommonParser
    from bytelang.impl.parser.package import PackageParser
    from bytelang.impl.semantizer.package import PackageSemanticContext
    from bytelang.impl.parser.env import EnvironmentParser

    def _process[S: CommonSemanticContext](code: str, parser_cls: type[CommonParser], context: S) -> S:
        _tokens = Lexer(TokenType.build_regex()).run(StringIO(code)).unwrap()
        print(_tokens)

        _program = Program.parse(parser_cls(OutputStream(tuple(_tokens)))).unwrap()
        print(_program)

        _program.accept(context).unwrap()
        return context

    def _pr(title: str, reg: MutableRegistry):
        print(f"{f" {title} ({len(tuple(reg.getItems()))}) ":-^40}")
        print("\n".join(map(str, reg.getItems())))

    try:

        package_code = """
        .inst foo(a: u8, b: *u8)
        .inst bar(array: [10]u8)
        """

        _global_macros = MutableImmediateRegistry(())
        _global_types = MutableImmediateRegistry((
            ("u8", PrimitiveTypeProfile(u8)),
        ))
        _global_constants = MutableImmediateRegistry(())

        my_package = _process(package_code, PackageParser, PackageSemanticContext(
            macro_registry=_global_macros,
            type_registry=_global_types,
            const_registry=_global_constants,
            instruction_registry=MutableImmediateRegistry(())
        ))

        _pr("Constants", my_package.const_registry)
        _pr("Macro", my_package.macro_registry)
        _pr("Types", my_package.type_registry)
        _pr("Instructions", my_package.instruction_registry)

        env_code = """
        .type u8_array = [10]u8
        .use package
        """

        env_context = _process(env_code, EnvironmentParser, EnvironmentSemanticContext(
            macro_registry=_global_macros,
            type_registry=_global_types,
            const_registry=_global_constants,
            package_registry=MutableImmediateRegistry((
                ("package", my_package.toBundle()),
            ))
        ))

        _pr("Constants", env_context.const_registry)
        _pr("Macro", env_context.macro_registry)
        _pr("Types", env_context.type_registry)
        _pr("Packages", env_context.package_registry)

    except Panic as e:
        print(e)

    return


if __name__ == '__main__':
    _test()
