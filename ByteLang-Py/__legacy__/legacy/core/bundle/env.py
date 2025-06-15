from dataclasses import dataclass

from bytelang.legacy.abc.profiles import EnvironmentInstructionProfile
from bytelang.legacy.abc.registry import Registry
from bytelang.legacy.core.bundle.pointer import PointersBundle


@dataclass(frozen=True)
class EnvironmentBundle:
    """Набор окружения"""

    instructions: Registry[str, EnvironmentInstructionProfile]
    """Инструкции окружения"""

    pointers: PointersBundle
    """набор указателей"""
