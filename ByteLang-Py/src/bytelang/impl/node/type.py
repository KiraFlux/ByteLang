from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable

from bytelang.abc.parser import Parser
from bytelang.core.tokens import TokenType
from bytelang.core.type import TypeProfile
from bytelang.impl.node.expression import Expression
from bytelang.impl.node.expression import Identifier
from bytelang.impl.node.super import HasExistingID
from bytelang.impl.node.super import HasIdentifier
from bytelang.impl.node.super import SuperNode
from bytelang.impl.semantizer.common import CommonSemanticContext
from rustpy.result import MultipleErrorsResult
from rustpy.result import Result


class Type(SuperNode[CommonSemanticContext, TypeProfile, 'Type'], ABC):
    """Узел типа"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Type, Iterable[str]]:
        return PureType.parse(parser)

    @abstractmethod
    def accept(self, context: CommonSemanticContext) -> Result[TypeProfile, Iterable[str]]:
        pass


@dataclass(frozen=True)
class PureType(Type, HasExistingID):
    """Чистый тип"""

    def accept(self, context: CommonSemanticContext) -> Result[TypeProfile, Iterable[str]]:
        return self.checkIdentifier(context.type_registry).map(err=lambda e: (e,))

    @classmethod
    def parse(cls, parser: Parser) -> Result[Type, Iterable[str]]:
        """Создать чистый тип на основе идентификатора"""
        return Identifier.parse(parser).map(lambda ok: cls(ok))


@dataclass(frozen=True)
class PointerType(Type):
    """Тип Указателя"""

    pointer: Type
    """Тип указателя"""

    def accept(self, context: CommonSemanticContext) -> Result[TypeProfile, Iterable[str]]:
        pass
        # TODO Здесь в профиле будет один тип для значений,
        #  а для самого указателя другой примитивный тип (
        #  какой? тот, что указан в контексте.
        #  PS я не могу пока узнать тип, поскольку это обобщенный контекст)


@dataclass(frozen=True)
class ArrayType(Type):
    """Тип Массив"""

    type: Type
    """Тип элементов массива"""
    length: Expression
    """Выражение, определяющее длину массива"""

    def accept(self, context: CommonSemanticContext) -> Result[TypeProfile, Iterable[str]]:
        ret = MultipleErrorsResult()

        element_type_profile = ret.putMulti(self.type.accept(context))
        array_length = ret.putMulti(self.length.accept(context))

        return ret.make(lambda: NotImplemented)


@dataclass(frozen=True)
class Field(SuperNode[CommonSemanticContext, tuple[Identifier, TypeProfile], "Field"], HasIdentifier):
    """Узел объявления поля"""

    type: Type
    """Тип поля"""

    def accept(self, context: CommonSemanticContext) -> Result[tuple[Identifier, TypeProfile], Iterable[str]]:
        ret = MultipleErrorsResult()
        type_profile = ret.putMulti(self.type.accept(context))
        return ret.make(lambda: (self.identifier, type_profile.unwrap()))

    @classmethod
    def parse(cls, parser: Parser) -> Result[Field, Iterable[str]]:
        """Парсинг токенов в поле"""
        ret = MultipleErrorsResult()

        name = ret.putSingle(Identifier.parse(parser))
        ret.putSingle(parser.consume(TokenType.Colon))
        pure = ret.putMulti(PureType.parse(parser))

        return ret.make(lambda: cls(name.unwrap(), pure.unwrap()))
