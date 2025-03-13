from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from typing import ClassVar
from typing import Final
from typing import TextIO
from typing import final

from bytelang.abc.registry import Registry
from bytelang.core.bundle.env import EnvironmentBundle
from bytelang.core.bundle.package import PackageBundle
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

    type PackageRegistry = Registry[str, PackageBundle]
    type EnvRegistry = Registry[str, EnvironmentBundle]

    type PackageLoader = Loader[EnvironmentBundle, EnvironmentSemanticContext]
    type EnvLoader = Loader[PackageBundle, PackageSemanticContext]
    type SketchLoader = Loader[SketchBundle, SketchSemanticContext]

    env_dir: ClassVar = Final[str]("envs")
    """Подкаталог окружений"""
    packages_dir: ClassVar = Final[str]("packages")
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

        common_context = CommonSemanticContext(self._primitives)

        package_registry = self._makePackageRegistry(self._makePackageLoader(common_context))
        env_registry = self._makeEnvRegistry(self._makeEnvLoader(common_context, package_registry))
        sketch_loader = self._makeSketchLoader(common_context, env_registry)

        return sketch_loader.load(source)

    def _makeLoader[P: CommonParser, S: SuperSemanticContext](
            self,
            common_context: CommonSemanticContext,
            parser_maker: Callable[[OutputStream[Token]], P],
            composite_context_maker: Callable[[CommonSemanticContext], S]
    ) -> Loader:
        return Loader(self._lexer, common_context, parser_maker, composite_context_maker)

    def _makePackageLoader(self, common: CommonSemanticContext) -> PackageLoader:
        return self._makeLoader(common, lambda tokens: PackageParser(tokens), lambda context: PackageSemanticContext(context))

    def _makePackageRegistry(self, loader: PackageLoader) -> PackageRegistry:
        return BundleLoaderRegistry(self._root_path / self.packages_dir, loader)

    def _makeEnvLoader(self, common: CommonSemanticContext, packages: PackageRegistry) -> EnvLoader:
        return self._makeLoader(common, lambda tokens: EnvironmentParser(tokens), lambda context: EnvironmentSemanticContext(context, self._primitives, packages))

    def _makeEnvRegistry(self, loader: EnvLoader) -> EnvRegistry:
        return BundleLoaderRegistry(self._root_path / self.env_dir, loader)

    def _makeSketchLoader(self, common: CommonSemanticContext, environments: EnvRegistry) -> SketchLoader:
        return self._makeLoader(common, lambda tokens: SketchParser(tokens), lambda context: SketchSemanticContext(context, environments))
