from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Callable
from typing import ClassVar
from typing import TextIO
from typing import final

from bytelang.legacy.core.bundle.sketch import SketchBundle
from bytelang.legacy.core.lexer import Lexer
from bytelang.legacy.core.loader import Loader
from bytelang.legacy.core.result import LogResult
from bytelang.legacy.core.stream import OutputStream
from bytelang.legacy.core.tokens import Token
from bytelang.legacy.core.tokens import TokenType
from bytelang.legacy.impl.parser.common import CommonParser
from bytelang.legacy.impl.parser.env import EnvironmentParser
from bytelang.legacy.impl.parser.package import PackageParser
from bytelang.legacy.impl.parser.sketch import SketchParser
from bytelang.legacy.impl.registry.loader import BundleLoaderRegistry
from bytelang.legacy.impl.registry.primitive import PrimitiveRegistry
from bytelang.legacy.impl.semantizer.common import CommonSemanticContext
from bytelang.legacy.impl.semantizer.env import EnvironmentSemanticContext
from bytelang.legacy.impl.semantizer.package import PackageSemanticContext
from bytelang.legacy.impl.semantizer.sketch import SketchSemanticContext
from bytelang.legacy.impl.semantizer.super import SuperSemanticContext


@final
@dataclass
class SketchCompiler:
    """Компилятор исходного кода скетча в набор"""

    env_dir: ClassVar = "envs"
    """Подкаталог окружений"""
    packages_dir: ClassVar = "packages"
    """Подкаталог пакетов"""

    _root_path: Path
    """Корневая директория ресурсов"""
    _lexer: Lexer
    """Лексический анализатор"""
    _primitives: PrimitiveRegistry
    """Реестр примитивных типов"""

    @classmethod
    def new(cls, path: Path) -> SketchCompiler:
        """Создать по упрощенной схеме"""
        return cls(path, Lexer(TokenType.build_regex()), PrimitiveRegistry())

    def run(self, source: TextIO) -> LogResult[SketchBundle]:
        """Обработать скетч в набор"""

        common = CommonSemanticContext(self._primitives)

        package_registry = BundleLoaderRegistry(
            self._root_path / self.packages_dir,
            self._makeLoader(
                common,
                PackageParser.new,
                lambda context: PackageSemanticContext(context)
            )
        )

        env_registry = BundleLoaderRegistry(
            self._root_path / self.env_dir,
            self._makeLoader(
                common,
                EnvironmentParser.new,
                lambda context: EnvironmentSemanticContext(context, self._primitives, package_registry)
            )
        )

        sketch_loader = self._makeLoader(
            common,
            SketchParser.new,
            lambda context: SketchSemanticContext(context, env_registry)
        )

        return sketch_loader.load(source)

    def _makeLoader(
            self,
            common_context: CommonSemanticContext,
            parser_maker: Callable[[OutputStream[Token]], CommonParser],
            composite_context_maker: Callable[[CommonSemanticContext], SuperSemanticContext]
    ) -> Loader:
        return Loader(self._lexer, common_context, parser_maker, composite_context_maker)


def _test():
    c = SketchCompiler.new(Path(r"E:\Projects\ByteLang\ByteLang-Py\res"))

    code = """
    
    .env esp32
    
    .var foo: [5]u8 = {}
    
    """

    sketch = c.run(StringIO(code))

    if sketch.isErr():
        print("\n".join(sketch.err().getItems()))
    else:
        print(sketch.unwrap())

    return


if __name__ == '__main__':
    _test()
