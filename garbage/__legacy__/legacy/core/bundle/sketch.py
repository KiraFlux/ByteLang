from dataclasses import dataclass

from bytelang.legacy.abc.profiles import VariableProfile
from bytelang.legacy.abc.registry import Registry


@dataclass(frozen=True)
class SketchBundle:
    """Набор скетча"""

    variables: Registry[str, VariableProfile]
    """Значения"""
