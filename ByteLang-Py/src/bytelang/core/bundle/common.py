from dataclasses import dataclass

from bytelang.abc.profiles import MacroProfile
from bytelang.abc.profiles import RValueProfile
from bytelang.abc.profiles import TypeProfile
from bytelang.abc.registry import Registry


@dataclass(frozen=True)
class CommonBundle:
    """Набор данных общего назначения"""

    constants: Registry[str, RValueProfile]
    """Константы"""

    marcos: Registry[str, MacroProfile]
    """Макросы"""

    types: Registry[str, TypeProfile]
    """Типы"""
