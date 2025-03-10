"""Набор данных пакета"""
from dataclasses import dataclass

from bytelang.abc.profiles import PackageInstructionProfile
from bytelang.abc.registry import Registry


@dataclass(frozen=True)
class PackageBundle:
    """Набор данных пакета"""

    instructions: Registry[str, PackageInstructionProfile]
    """Инструкции"""
