"""Контекст семантического анализа файла окружения"""

from dataclasses import dataclass

from bytelang.abc.profiles import EnvironmentInstructionProfile
from bytelang.abc.registry import MutableRegistry
from bytelang.core.bundle.env import EnvironmentBundle
from bytelang.core.bundle.package import PackageBundle
from bytelang.core.bundle.pointer import PointerBundle
from bytelang.impl.semantizer.common import CommonSemanticContext


@dataclass
class EnvironmentSemanticContext(CommonSemanticContext[EnvironmentBundle]):
    """Контекст семантического анализа файла окружения"""

    package_registry: MutableRegistry[str, PackageBundle]
    """Реестр пакетов"""

    instruction_registry: MutableRegistry[str, EnvironmentInstructionProfile]
    """Реестр инструкций окружения"""

    pointers: PointerBundle
    """Набор указателей"""

    def toBundle(self) -> EnvironmentBundle:
        pass


def _test():
    from io import StringIO

    from bytelang.core.stream import OutputStream
    from bytelang.core.lexer import Lexer
    from bytelang.core.tokens import TokenType
    from bytelang.impl.node.program import Program
    from bytelang.impl.registry.immediate import MutableImmediateRegistry
    from bytelang.impl.serializer.primitive import u8
    from bytelang.impl.serializer.primitive import u16
    from bytelang.impl.serializer.primitive import i8
    from bytelang.impl.profiles.type import PrimitiveTypeProfile
    from bytelang.impl.parser.common import CommonParser
    from bytelang.impl.parser.package import PackageParser
    from bytelang.impl.parser.env import EnvironmentParser
    from bytelang.impl.semantizer.package import PackageSemanticContext
    from bytelang.impl.registry.primitive import PrimitiveRegistry

    from rustpy.exceptions import Panic

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
        .type u8_array = [10]u8
        
        .inst foo(a: u8, b: *u8)
        .inst bar(array: u8_array)
        """

        _primitive_registry = PrimitiveRegistry()

        _global_macros = MutableImmediateRegistry(())

        _global_types = MutableImmediateRegistry((
            (_id, PrimitiveTypeProfile(_primitive))
            for (_id, _primitive) in _primitive_registry.getItems()
        ))

        _global_constants = MutableImmediateRegistry(())

        my_package = _process(package_code, PackageParser, PackageSemanticContext(
            macro_registry=_global_macros,
            type_registry=_global_types,
            const_registry=_global_constants,
            instruction_registry=MutableImmediateRegistry(())
        ))

        # _pr("Constants", my_package.const_registry)
        # _pr("Macro", my_package.macro_registry)
        # _pr("Types", my_package.type_registry)
        _pr("Instructions", my_package.instruction_registry)

        env_code = """
        
        .use package{bar}
        .use package{foo}
        """

        env_context = _process(env_code, EnvironmentParser, EnvironmentSemanticContext(
            macro_registry=_global_macros,
            type_registry=_global_types,
            const_registry=_global_constants,
            package_registry=MutableImmediateRegistry((
                ("package", my_package.toBundle()),
            )),
            instruction_registry=MutableImmediateRegistry(()),
            pointers=PointerBundle(  # TODO создать специальные директивы для указания ширин указателей
                instruction_call_pointer=u8,
                program_mark_pointer=u16,
                data_section_pointer=i8
            )
        ))

        _pr("Constants", env_context.const_registry)
        _pr("Macro", env_context.macro_registry)
        _pr("Types", env_context.type_registry)
        _pr("Packages", env_context.package_registry)
        _pr("Instructions", env_context.instruction_registry)

    except Panic as e:
        print(e)

    return


if __name__ == '__main__':
    _test()
