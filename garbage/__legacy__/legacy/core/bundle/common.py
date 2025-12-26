from dataclasses import dataclass

from bytelang.legacy.abc.profiles import MacroProfile
from bytelang.legacy.abc.profiles import RValueProfile
from bytelang.legacy.abc.profiles import TypeProfile
from bytelang.legacy.abc.registry import Registry


@dataclass(frozen=True)
class CommonBundle:
    """Набор данных общего назначения"""

    constants: Registry[str, RValueProfile]
    """Константы"""

    marcos: Registry[str, MacroProfile]
    """Макросы"""

    types: Registry[str, TypeProfile]
    """Типы"""
