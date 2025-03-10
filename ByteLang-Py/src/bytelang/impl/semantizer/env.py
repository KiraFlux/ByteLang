"""Контекст семантического анализа файла окружения"""

from dataclasses import dataclass
from typing import Optional

from bytelang.abc.profiles import EnvironmentInstructionProfile
from bytelang.abc.registry import MutableRegistry
from bytelang.abc.registry import Registry
from bytelang.abc.serializer import Serializer
from bytelang.core.bundle.env import EnvironmentBundle
from bytelang.core.bundle.package import PackageBundle
from bytelang.core.bundle.pointer import PointersBundle
from bytelang.impl.semantizer.common import CommonSemanticContext


@dataclass
class EnvironmentSemanticContext(CommonSemanticContext[EnvironmentBundle]):
    """Контекст семантического анализа файла окружения"""

    package_registry: Registry[str, PackageBundle, str]
    """Реестр пакетов"""

    instruction_registry: MutableRegistry[str, EnvironmentInstructionProfile, str]
    """Реестр инструкций окружения"""

    primitive_serializers_registry: Registry[str, Serializer, str]
    """Реестр сериализаторов примитивных типов"""

    instruction_pointer: Optional[Serializer[int]] = None
    """Сериализатор указателя на инструкцию"""

    program_pointer: Optional[Serializer[int]] = None
    """Сериализатор указателя на область программы"""

    data_pointer: Optional[Serializer[int]] = None
    """Сериализатор указателя в секции данных"""

    def toBundle(self) -> EnvironmentBundle:
        return EnvironmentBundle(
            instructions=self.instruction_registry,
            pointers=PointersBundle(
                instruction_call_pointer=self.instruction_pointer,
                program_mark_pointer=self.program_pointer,
                data_section_pointer=self.data_pointer
            )
        )


def _test():
    from io import StringIO

    from bytelang.core.stream import OutputStream
    from bytelang.core.lexer import Lexer
    from bytelang.core.tokens import TokenType
    from bytelang.impl.node.program import Program
    from bytelang.impl.registry.immediate import MutableImmediateRegistry
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

        pass

        return context

    def _pr(title: str, reg: Registry):
        print(f"{f" {title} ({len(tuple(reg.getItems()))}) ":-^40}")
        print("\n".join(map(str, reg.getItems())))

    try:

        package_code = """
        .macro foo() -> 12345
        .const foo = @foo()
        .type alias = *u8
        .struct FooBar { x: f32, y: f32 }
        
        .inst go(a: alias, b: [foo]u8)
        
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

        _pr("Instructions", my_package.instruction_registry)

        env_code = """
        
        .ptr_inst u8
    
        .use package
        """

        env_context = _process(env_code, EnvironmentParser, EnvironmentSemanticContext(
            macro_registry=_global_macros,
            type_registry=_global_types,
            const_registry=_global_constants,
            package_registry=MutableImmediateRegistry((
                ("package", my_package.toBundle()),
            )),
            instruction_registry=MutableImmediateRegistry(()),
            primitive_serializers_registry=_primitive_registry
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
