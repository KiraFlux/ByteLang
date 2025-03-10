"""Набор данных пакета"""
from dataclasses import dataclass

from bytelang.abc.profiles import PackageInstructionProfile
from bytelang.abc.registry import Registry
from bytelang.core.bundle.common import CommonBundle


@dataclass(frozen=True)
class PackageBundle(CommonBundle):
    """Набор данных пакета"""

    instructions: Registry[str, PackageInstructionProfile]
    """Инструкции"""
