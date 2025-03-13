"""Контекст семантического анализа файла окружения"""

from __future__ import annotations

from typing import Final
from typing import Optional
from typing import final

from bytelang.abc.profiles import EnvironmentInstructionProfile
from bytelang.abc.registry import Registry
from bytelang.abc.serializer import Serializer
from bytelang.core.bundle.env import EnvironmentBundle
from bytelang.core.bundle.package import PackageBundle
from bytelang.core.bundle.pointer import PointersBundle
from bytelang.impl.registry.immediate import MutableImmediateRegistry
from bytelang.impl.semantizer.common import CommonSemanticContext
from bytelang.impl.semantizer.composite import CompositeSemanticContext


@final
class EnvironmentSemanticContext(CompositeSemanticContext[EnvironmentBundle]):
    """Контекст семантического анализа файла окружения"""

    def __init__(self, common: CommonSemanticContext, primitives: Registry[str, Serializer], packages: Registry[str, PackageBundle]) -> None:
        super().__init__(common)

        self.primitive_serializers_registry: Final = primitives
        """Реестр сериализаторов примитивных типов"""
        self.package_registry: Final = packages
        """Реестр пакетов"""

        self.instruction_registry: Final = MutableImmediateRegistry[str, EnvironmentInstructionProfile](())
        """Реестр инструкций окружения"""

        self.instruction_pointer: Optional[Serializer[int]] = None
        """Сериализатор указателя на инструкцию"""
        self.program_pointer: Optional[Serializer[int]] = None
        """Сериализатор указателя на область программы"""
        self.data_pointer: Optional[Serializer[int]] = None
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
    from bytelang.impl.parser.package import PackageParser
    from bytelang.impl.parser.env import EnvironmentParser
    from bytelang.impl.semantizer.package import PackageSemanticContext
    from bytelang.impl.registry.primitive import PrimitiveRegistry
    from bytelang.core.lexer import Lexer
    from bytelang.core.tokens import TokenType
    from bytelang.core.loader import Loader
    from bytelang.impl.registry.loader import BundleLoaderRegistry

    from rustpy.exceptions import Panic
    from pathlib import Path

    root_path = Path(r"A:\Projects\ByteLang\ByteLang-Py\res")
    _lexer = Lexer(TokenType.build_regex())
    _primitive_registry = PrimitiveRegistry()


    _common_context = CommonSemanticContext(_primitive_registry)

    package_loader = BundleLoaderRegistry[PackageBundle, PackageSemanticContext](
        root_path / "packages",
        Loader(
            _lexer,
            _common_context,
            lambda tokens: PackageParser(tokens),
            lambda context: PackageSemanticContext(context)
        )
    )

    env_loader = BundleLoaderRegistry[EnvironmentBundle, EnvironmentSemanticContext](
        root_path / "envs",
        Loader(
            _lexer,
            _common_context,
            lambda tokens: EnvironmentParser(tokens),
            lambda context: EnvironmentSemanticContext(context, _primitive_registry, package_loader)
        )
    )

    def _pr(title: str, reg: Registry):
        print(f"{f" <<< {title} : {len(tuple(reg.getItems()))} >>> ":-^40}")
        print("\n".join(map(str, reg.getItems())))

    try:
        _my_env = env_loader.get("test_env").unwrap()

        _pr("Constants", _common_context.getConstants())
        _pr("Macro", _common_context.getMacros())
        _pr("Types", _common_context.getTypes())
        _pr("Packages", package_loader)
        _pr("Instructions", _my_env.instructions)

    except Panic as e:
        print(e)

    return


if __name__ == '__main__':
    _test()
