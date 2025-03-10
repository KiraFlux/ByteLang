from __future__ import annotations

from dataclasses import dataclass

from bytelang.abc.serializer import Serializer


@dataclass(frozen=True)
class PointersBundle:
    """Набор указателей"""

    instruction_call_pointer: Serializer[int]
    """Примитивный тип, определяющий ширину указателя на код инструкции в таблице"""

    program_mark_pointer: Serializer[int]
    """примитивный тип, определяющий ширину указателя на метку в коде"""

    data_section_pointer: Serializer[int]
    """примитивный тип, определяющий ширину указателя на элемент в секции данных"""
