from abc import ABC

from bytelang.abc.serializer import Serializable
from bytelang.abc.serializer import Serializer


class TypeProfile[T: Serializable](ABC):
    """Профиль типа"""
    # TODO решить почему он не должен схлопнуться. Возможно будет удобно приводить типы.. (тут нужно хранить указатели)
    serializer: Serializer[T]
