from dataclasses import dataclass
from typing import Iterable
from typing import Mapping
from typing import Sequence

from bytelang.abc.profiles import RValueProfile
from bytelang.abc.profiles import TypeProfile
from bytelang.abc.semantic import SemanticContext
from bytelang.abc.serializer import Serializable
from bytelang.core.LEGACY_result import LEGACY_Result
from bytelang.core.LEGACY_result import LEGACYResultAccumulator
from bytelang.core.LEGACY_result import SingleLEGACYResult
from bytelang.impl.semantizer.sketch import SketchSemanticContext
from bytelang.impl.serializer.primitive import PrimitiveSerializer


@dataclass(frozen=True)
class PrimitiveTypeProfile[T: Serializable](TypeProfile[SemanticContext]):
    """Профиль чистого типа"""

    _serializer: PrimitiveSerializer[T]
    """Сериализатор"""

    def apply(self, rvalue: RValueProfile[T], context: SemanticContext) -> LEGACY_Result[bytes, Iterable[str]]:
        return self._serializer.pack(rvalue.getValue())


@dataclass(frozen=True)
class PointerTypeProfile[T: Serializable](TypeProfile[SketchSemanticContext]):
    """Профиль указательного типа"""

    _pointer_type: TypeProfile
    """Профиль типа на который ведет указатель"""

    def apply(self, rvalue: RValueProfile[T], context: SketchSemanticContext) -> LEGACY_Result[bytes, Iterable[str]]:
        raise NotImplementedError


@dataclass(frozen=True)
class ArrayTypeProfile[T: Serializable](TypeProfile[SemanticContext]):
    """Профиль типа массива"""

    _item_type_profile: TypeProfile
    """Профиль типа элемента"""
    _length: int
    """Длина массива"""

    def apply(self, rvalue: RValueProfile[Sequence[T]], context: SemanticContext) -> LEGACY_Result[bytes, Iterable[str]]:
        items = rvalue.getValue()

        if (got := items) != self._length:
            return SingleLEGACYResult.error((f"Invalid array init items: {got}",))

        ret = LEGACYResultAccumulator()

        for rvalue_item in items:
            ret.putMulti(self._item_type_profile.apply(rvalue_item, context))

        return ret.map(lambda packed_items: b"".join(packed_items))


@dataclass(frozen=True)
class StructTypeProfile(TypeProfile[SemanticContext]):
    """Профиль структурного типа"""

    _fields: Mapping[str, TypeProfile]
    """Поля структуры"""

    def apply(self, rvalue: RValueProfile[Sequence[Serializable]], context: SemanticContext) -> LEGACY_Result[bytes, Iterable[str]]:
        items = rvalue.getValue()

        if (got := items) != len(self._fields):
            return SingleLEGACYResult.error((f"Invalid array init items: {got}",))

        ret = LEGACYResultAccumulator()

        for field, rvalue_item in zip(self._fields.values(), items):
            ret.putMulti(field.apply(rvalue_item, context))

        return ret.map(lambda packed_items: b"".join(packed_items))
