from typing import Optional
from typing import final

from bytelang.legacy.abc.profiles import RValueProfile
from bytelang.legacy.abc.profiles import TypeProfile
from bytelang.legacy.abc.profiles import VariableProfile
from bytelang.legacy.abc.registry import Registry
from bytelang.legacy.core.bundle.env import EnvironmentBundle
from bytelang.legacy.core.bundle.sketch import SketchBundle
from bytelang.legacy.core.result import ErrOne
from bytelang.legacy.core.result import LogResult
from bytelang.legacy.core.result import Ok
from bytelang.legacy.core.stream import InputStream
from bytelang.legacy.impl.registry.immediate import MutableImmediateRegistry
from bytelang.legacy.impl.semantizer.common import CommonSemanticContext
from bytelang.legacy.impl.semantizer.composite import CompositeSemanticContext


@final
class SketchSemanticContext(CompositeSemanticContext[SketchBundle]):
    """Контекст семантического анализа скетча"""

    def __init__(self, common: CommonSemanticContext, environments: Registry[str, EnvironmentBundle]) -> None:
        super().__init__(common)

        self.environment_registry = environments
        """Реестр окружений"""

        self.selected_environment: Optional[EnvironmentBundle] = None
        """Выбранное окружение"""

        self.mark_registry = MutableImmediateRegistry[str, RValueProfile](())
        """Реестр меток"""

        self._var_registry = MutableImmediateRegistry[str, VariableProfile](())
        """Реестр значений"""

        self.instructions_code = InputStream[NotImplemented]
        """Код инструкций"""

    def addVar[T](self, key: str, _type: TypeProfile, _init: RValueProfile[T]) -> LogResult[None]:
        if self._var_registry.has(key):
            return ErrOne(f"{key} already has")

        if self.selected_environment is None:
            return ErrOne(f"{self.selected_environment=}")

        current_var_address = sum(v.getSize(self) for v in self._var_registry.getMappingView().values())

        from bytelang.legacy.impl.profiles.rvalue import IntegerRV

        self._var_registry.register(key, VariableProfile(_type, _init, IntegerRV(current_var_address)))

        return Ok(None)

    def toBundle(self) -> SketchBundle:
        return SketchBundle(
            variables=self._var_registry
        )
