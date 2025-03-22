from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Callable
from typing import ClassVar
from typing import TextIO
from typing import final

from bytelang.core.bundle.sketch import SketchBundle
from bytelang.core.lexer import Lexer
from bytelang.core.loader import Loader
from bytelang.core.result import LogResult
from bytelang.core.stream import OutputStream
from bytelang.core.tokens import Token
from bytelang.core.tokens import TokenType
from bytelang.impl.parser.common import CommonParser
from bytelang.impl.parser.env import EnvironmentParser
from bytelang.impl.parser.package import PackageParser
from bytelang.impl.parser.sketch import SketchParser
from bytelang.impl.registry.loader import BundleLoaderRegistry
from bytelang.impl.registry.primitive import PrimitiveRegistry
from bytelang.impl.semantizer.common import CommonSemanticContext
from bytelang.impl.semantizer.env import EnvironmentSemanticContext
from bytelang.impl.semantizer.package import PackageSemanticContext
from bytelang.impl.semantizer.sketch import SketchSemanticContext
from bytelang.impl.semantizer.super import SuperSemanticContext


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
    c = SketchCompiler.new(Path(r"A:\Projects\ByteLang\ByteLang-Py\res"))

    code = """
    
    .env arduino
    
    digitalRead 2, 0
    
    """

    sketch = c.run(StringIO(code))

    if sketch.isErr():
        print("\n".join(sketch.err().getItems()))
    else:
        print(sketch.unwrap())

    return


if __name__ == '__main__':
    _test()
