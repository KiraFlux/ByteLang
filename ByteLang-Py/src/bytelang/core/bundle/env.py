from dataclasses import dataclass

from bytelang.abc.profiles import EnvironmentInstructionProfile
from bytelang.abc.registry import Registry
from bytelang.core.bundle.pointer import PointersBundle


@dataclass(frozen=True)
class EnvironmentBundle:
    """Набор окружения"""

    instructions: Registry[str, EnvironmentInstructionProfile, str]
    """Инструкции окружения"""

    pointers: PointersBundle
    """набор указателей"""
