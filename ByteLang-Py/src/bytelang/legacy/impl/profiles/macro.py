from dataclasses import dataclass
from typing import Sequence

from bytelang.legacy.abc.profiles import MacroProfile
from bytelang.legacy.core.result import ErrOne
from bytelang.legacy.core.result import LogResult
from bytelang.legacy.core.result import Ok
from bytelang.legacy.impl.node.expression import Expression
from bytelang.legacy.impl.node.expression import Identifier


@dataclass(frozen=True)
class MacroProfileImpl(MacroProfile[Expression]):
    """Реализация профиля макроса"""

    arguments: Sequence[Identifier]
    template: Expression

    def expand(self, arguments: Sequence[Expression]) -> LogResult[Expression]:
        if (len_got := len(arguments)) != (len_expected := len(self.arguments)):
            return ErrOne(f"Expected: {len_expected} ({self.arguments}), got: {len_got} ({arguments})")

        return Ok(self.template.expand({key: expr for key, expr in zip(self.arguments, arguments)}))
