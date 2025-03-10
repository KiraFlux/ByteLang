from bytelang.abc.profiles import EnvironmentInstructionProfile
from bytelang.abc.registry import Registry
from bytelang.core.bundle.common import CommonBundle


class EnvironmentBundle(CommonBundle):
    """Набор окружения"""

    instructions: Registry[str, EnvironmentInstructionProfile]
