from dataclasses import dataclass
from typing import Iterable
from typing import Optional

from bytelang.abc.profiles import RValueProfile
from bytelang.abc.registry import MutableRegistry
from bytelang.abc.registry import Registry
from bytelang.abc.semantic import SemanticContext
from bytelang.core.bundle.env import EnvironmentBundle
from bytelang.impl.semantizer.common import CommonSemanticContext


@dataclass
class SketchSemanticContext(CommonSemanticContext, SemanticContext[NotImplemented]):
    """Контекст семантического анализа скетча"""

    environment_registry: Registry[str, EnvironmentBundle]
    """Реестр окружений"""

    selected_environment: Optional[EnvironmentBundle]
    """Выбранное окружение"""

    mark_registry: MutableRegistry[str, RValueProfile]
    """Реестр меток"""

    instructions_code: bytearray  # todo Byte Stream
    """Код инструкций"""

    def toBundle(self) -> None:
        pass


def _test():
    from bytelang.impl.registry.immediate import MutableImmediateRegistry
    from bytelang.impl.profiles.type import PrimitiveTypeProfile
    from bytelang.impl.parser.package import PackageParser
    from bytelang.impl.parser.env import EnvironmentParser
    from bytelang.impl.semantizer.package import PackageSemanticContext
    from bytelang.impl.registry.primitive import PrimitiveRegistry
    from bytelang.core.lexer import Lexer
    from bytelang.core.tokens import TokenType
    from bytelang.core.loader import Loader
    from bytelang.impl.parser.sketch import SketchParser
    from bytelang.impl.registry.loader import CodeLoadingRegistry
    from bytelang.core.bundle.package import PackageBundle
    from bytelang.impl.semantizer.env import EnvironmentSemanticContext

    from rustpy.exceptions import Panic
    from pathlib import Path

    root_path = Path(r"A:\Projects\ByteLang\ByteLang-Py\res")

    _lexer = Lexer(TokenType.build_regex())

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
        root_path / "packages",
        Loader(
            _lexer,
            _common_context,
            lambda tokens: PackageParser(tokens),
            lambda context: PackageSemanticContext(
                macro_registry=context.macro_registry,
                type_registry=context.type_registry,
                const_registry=context.const_registry,
                instruction_registry=MutableImmediateRegistry(())
            )
        )
    )

    env_loader = CodeLoadingRegistry[EnvironmentBundle, EnvironmentSemanticContext](
        root_path / "envs",
        Loader(
            _lexer,
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
    )

    sketch_loader = Loader(
        _lexer,
        _common_context,
        lambda tokens: SketchParser(tokens),
        lambda context: SketchSemanticContext(
            macro_registry=context.macro_registry,
            type_registry=context.type_registry,
            const_registry=context.const_registry,
            environment_registry=env_loader,
            mark_registry=MutableImmediateRegistry(()),
            selected_environment=None,
            instructions_code=bytearray(),
        )
    )

    def _pr(title: str, reg: Registry):
        print(f"{f" <<< {title} : {len(tuple(reg.getItems()))} >>> ":-^40}")
        print("\n".join(map(str, reg.getItems())))

    try:
        with open(root_path / "sketches" / "sketch.bls") as source:
            sketch = sketch_loader.load(source).unwrap()

        _pr("Constants", _common_context.const_registry)
        _pr("Macro", _common_context.macro_registry)
        _pr("Types", _common_context.type_registry)
        _pr("Packages", package_loader)
        # _pr("Environments", sketch)

    except Panic as e:
        print(e)

    return


if __name__ == '__main__':
    _test()
