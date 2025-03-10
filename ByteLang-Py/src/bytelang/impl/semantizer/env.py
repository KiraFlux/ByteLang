"""Контекст семантического анализа файла окружения"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from bytelang.abc.profiles import EnvironmentInstructionProfile
from bytelang.abc.registry import MutableRegistry
from bytelang.abc.registry import Registry
from bytelang.abc.semantic import SemanticContext
from bytelang.abc.serializer import Serializer
from bytelang.core.bundle.env import EnvironmentBundle
from bytelang.core.bundle.package import PackageBundle
from bytelang.core.bundle.pointer import PointersBundle
from bytelang.impl.registry.loader import CodeLoadingRegistry
from bytelang.impl.semantizer.common import CommonSemanticContext


@dataclass
class EnvironmentSemanticContext(CommonSemanticContext, SemanticContext[EnvironmentBundle]):
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
    from bytelang.impl.registry.immediate import MutableImmediateRegistry
    from bytelang.impl.profiles.type import PrimitiveTypeProfile
    from bytelang.impl.parser.package import PackageParser
    from bytelang.impl.parser.env import EnvironmentParser
    from bytelang.impl.semantizer.package import PackageSemanticContext
    from bytelang.impl.registry.primitive import PrimitiveRegistry

    from rustpy.exceptions import Panic

    from pathlib import Path

    path = Path(r"A:\Projects\ByteLang\ByteLang-Py\res\test")

    _primitive_registry = PrimitiveRegistry()

    _common_context = CommonSemanticContext(
        macro_registry=MutableImmediateRegistry(()),
        type_registry=MutableImmediateRegistry((
            (_id, PrimitiveTypeProfile(_primitive))
            for (_id, _primitive) in _primitive_registry.getItems()
        )),
        const_registry=MutableImmediateRegistry(()),
    )

    package_loader = CodeLoadingRegistry[PackageBundle, PackageSemanticContext](
        path,
        _common_context,
        lambda tokens: PackageParser(tokens),
        lambda context: PackageSemanticContext(
            macro_registry=context.macro_registry,
            type_registry=context.type_registry,
            const_registry=context.const_registry,
            instruction_registry=MutableImmediateRegistry(())
        )
    )

    env_loader = CodeLoadingRegistry[EnvironmentBundle, EnvironmentSemanticContext](
        path,
        _common_context,
        lambda tokens: EnvironmentParser(tokens),
        lambda context: EnvironmentSemanticContext(
            macro_registry=context.macro_registry,
            type_registry=context.type_registry,
            const_registry=context.const_registry,
            package_registry=package_loader,
            instruction_registry=MutableImmediateRegistry(()),
            primitive_serializers_registry=_primitive_registry
        )
    )

    def _pr(title: str, reg: Registry):
        print(f"{f" {title} ({len(tuple(reg.getItems()))}) ":-^40}")
        print("\n".join(map(str, reg.getItems())))

    try:
        _my_env = env_loader.get("test_env").unwrap()

        _pr("Constants", _common_context.const_registry)
        _pr("Macro", _common_context.macro_registry)
        _pr("Types", _common_context.type_registry)
        _pr("Packages", package_loader)
        _pr("Instructions", _my_env.instructions)

    except Panic as e:
        print(e)

    return


if __name__ == '__main__':
    _test()
