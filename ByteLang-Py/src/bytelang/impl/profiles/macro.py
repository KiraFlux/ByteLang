from dataclasses import dataclass
from typing import Sequence

from bytelang.abc.profiles import MacroProfile
from bytelang.core.LEGACY_result import LEGACY_Result
from bytelang.core.LEGACY_result import SingleLEGACYResult
from bytelang.impl.node.expression import Expression
from bytelang.impl.node.expression import Identifier


@dataclass(frozen=True)
class MacroProfileImpl(MacroProfile[Expression]):
    """Реализация профиля макроса"""

    arguments: Sequence[Identifier]
    template: Expression

    def expand(self, arguments: Sequence[Expression]) -> LEGACY_Result[Expression, str]:
        if (len_got := len(arguments)) != (len_expected := len(self.arguments)):
            return SingleLEGACYResult.error(f"Expected: {len_expected} ({self.arguments}), got: {len_got} ({arguments})")

        return SingleLEGACYResult.ok(self.template.expand({key: expr for key, expr in zip(self.arguments, arguments)}))
