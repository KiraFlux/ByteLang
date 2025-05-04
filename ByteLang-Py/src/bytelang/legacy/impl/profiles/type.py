from dataclasses import dataclass
from typing import Mapping
from typing import Sequence

from bytelang.legacy.abc.profiles import RValueProfile
from bytelang.legacy.abc.profiles import TypeProfile
from bytelang.legacy.abc.semantic import SemanticContext
from bytelang.legacy.abc.serializer import Serializable
from bytelang.legacy.core.result import ErrOne
from bytelang.legacy.core.result import LogResult
from bytelang.legacy.core.result import ResultAccumulator
from bytelang.legacy.impl.semantizer.sketch import SketchSemanticContext
from bytelang.legacy.impl.serializer.primitive import PrimitiveSerializer


@dataclass(frozen=True)
class PrimitiveTypeProfile[T: Serializable](TypeProfile[SemanticContext]):
    """Профиль чистого типа"""

    _serializer: PrimitiveSerializer[T]
    """Сериализатор"""

    def getSize(self, context: SemanticContext) -> int:
        return self._serializer.getSize()

    def pack(self, rvalue: RValueProfile[T], context: SemanticContext) -> LogResult[bytes]:
        return self._serializer.pack(rvalue.getValue())


@dataclass(frozen=True)
class PointerTypeProfile[T: Serializable](TypeProfile[SketchSemanticContext]):
    """Профиль указательного типа"""

    _pointer_type: TypeProfile
    """Профиль типа на который ведет указатель"""

    def getSize(self, context: SketchSemanticContext) -> int:
        return context.selected_environment.pointers.data_section_pointer.getSize()

    def pack(self, rvalue: RValueProfile[T], context: SketchSemanticContext) -> LogResult[bytes]:
        raise NotImplementedError


@dataclass(frozen=True)
class ArrayTypeProfile[T: Serializable](TypeProfile[SemanticContext]):
    """Профиль типа массива"""

    _item_type_profile: TypeProfile
    """Профиль типа элемента"""
    _length: int
    """Длина массива"""

    def getSize(self, context: SemanticContext) -> int:
        return self._length * self._item_type_profile.getSize(context)

    def pack(self, rvalue: RValueProfile[Sequence[T]], context: SemanticContext) -> LogResult[bytes]:
        items = rvalue.getValue()

        if (got := items) != self._length:
            return ErrOne(f"Invalid array init items: {got}")

        ret = ResultAccumulator()

        for rvalue_item in items:
            ret.put(self._item_type_profile.pack(rvalue_item, context))

        return ret.map(lambda packed_items: b"".join(packed_items))


@dataclass(frozen=True)
class StructTypeProfile(TypeProfile[SemanticContext]):
    """Профиль структурного типа"""

    _fields: Mapping[str, TypeProfile]
    """Поля структуры"""

    def getSize(self, context: SemanticContext) -> int:
        return sum(f.getSize(context) for f in self._fields.values())

    def pack(self, rvalue: RValueProfile[Sequence[Serializable]], context: SemanticContext) -> LogResult[bytes]:
        items = rvalue.getValue()

        if (got := items) != len(self._fields):
            return ErrOne(f"Invalid array init items: {got}")

        ret = ResultAccumulator()

        for field, rvalue_item in zip(self._fields.values(), items):
            ret.put(field.pack(rvalue_item, context))

        return ret.map(lambda packed_items: b"".join(packed_items))
