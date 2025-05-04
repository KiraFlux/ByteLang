"""Набор данных пакета"""
from dataclasses import dataclass

from bytelang.legacy.abc.profiles import PackageInstructionProfile
from bytelang.legacy.abc.registry import Registry


@dataclass(frozen=True)
class PackageBundle:
    """Набор данных пакета"""

    instructions: Registry[str, PackageInstructionProfile]
    """Инструкции"""
