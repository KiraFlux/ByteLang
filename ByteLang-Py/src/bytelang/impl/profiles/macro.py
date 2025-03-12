from dataclasses import dataclass
from typing import Sequence

from bytelang.abc.profiles import MacroProfile
from bytelang.core.result import ErrOne
from bytelang.core.result import LogResult
from bytelang.core.result import Ok
from bytelang.impl.node.expression import Expression
from bytelang.impl.node.expression import Identifier


@dataclass(frozen=True)
class MacroProfileImpl(MacroProfile[Expression]):
    """Реализация профиля макроса"""

    arguments: Sequence[Identifier]
    template: Expression

    def expand(self, arguments: Sequence[Expression]) -> LogResult[Expression]:
        if (len_got := len(arguments)) != (len_expected := len(self.arguments)):
            return ErrOne(f"Expected: {len_expected} ({self.arguments}), got: {len_got} ({arguments})")

        return Ok(self.template.expand({key: expr for key, expr in zip(self.arguments, arguments)}))
