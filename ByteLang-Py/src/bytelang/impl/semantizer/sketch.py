from typing import Optional
from typing import final

from bytelang.abc.profiles import RValueProfile
from bytelang.abc.registry import Registry
from bytelang.core.bundle.env import EnvironmentBundle
from bytelang.impl.registry.immediate import MutableImmediateRegistry
from bytelang.impl.semantizer.common import CommonSemanticContext
from bytelang.impl.semantizer.composite import CompositeSemanticContext


@final
class SketchSemanticContext(CompositeSemanticContext[NotImplemented]):
    """Контекст семантического анализа скетча"""

    def __init__(self, common: CommonSemanticContext, environments: Registry[str, EnvironmentBundle]) -> None:
        super().__init__(common)
        self.environment_registry = environments
        """Реестр окружений"""
        self.selected_environment: Optional[EnvironmentBundle] = None
        """Выбранное окружение"""
        self.mark_registry = MutableImmediateRegistry[str, RValueProfile](())
        """Реестр меток"""
        self.instructions_code = bytearray()  # todo Byte Stream
        """Код инструкций"""

    def toBundle(self) -> None:
        pass


def _test():
    from bytelang.impl.parser.package import PackageParser
    from bytelang.impl.parser.env import EnvironmentParser
    from bytelang.impl.parser.sketch import SketchParser
    from bytelang.impl.semantizer.package import PackageSemanticContext
    from bytelang.impl.registry.primitive import PrimitiveRegistry
    from bytelang.core.lexer import Lexer
    from bytelang.core.tokens import TokenType
    from bytelang.core.loader import Loader
    from bytelang.impl.registry.loader import CodeLoadingRegistry
    from rustpy.exceptions import Panic
    from pathlib import Path
    from bytelang.impl.semantizer.env import EnvironmentSemanticContext
    from bytelang.core.bundle.package import PackageBundle

    root_path = Path(r"A:\Projects\ByteLang\ByteLang-Py\res")

    _lexer = Lexer(TokenType.build_regex())

    _primitive_registry = PrimitiveRegistry()

    _common_context = CommonSemanticContext(_primitive_registry)

    package_loader = CodeLoadingRegistry[PackageBundle, PackageSemanticContext](
        root_path / "packages",
        Loader(
            _lexer,
            _common_context,
            lambda tokens: PackageParser(tokens),
            lambda context: PackageSemanticContext(context)
        )
    )

    env_loader = CodeLoadingRegistry[EnvironmentBundle, EnvironmentSemanticContext](
        root_path / "envs",
        Loader(
            _lexer,
            _common_context,
            lambda tokens: EnvironmentParser(tokens),
            lambda context: EnvironmentSemanticContext(context, _primitive_registry, package_loader)
        )
    )

    sketch_loader = Loader(
        _lexer,
        _common_context,
        lambda tokens: SketchParser(tokens),
        lambda context: SketchSemanticContext(context, env_loader)
    )

    def _pr(title: str, reg: Registry):
        print(f"{f" <<< {title} : {len(tuple(reg.getItems()))} >>> ":-^40}")
        print("\n".join(map(str, reg.getItems())))

    try:
        _my_env = env_loader.get("test_env").unwrap()

        with open(root_path / "sketches" / "sketch.bls") as source:
            sketch = sketch_loader.load(source).unwrap()

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
