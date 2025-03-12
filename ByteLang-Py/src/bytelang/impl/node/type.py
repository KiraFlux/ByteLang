from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable

from bytelang.abc.parser import Parser
from bytelang.abc.profiles import TypeProfile
from bytelang.core.LEGACY_result import MultiErrorLEGACYResult
from bytelang.core.LEGACY_result import LEGACY_Result
from bytelang.core.tokens import TokenType
from bytelang.impl.node.expression import Expression
from bytelang.impl.node.expression import HasExistingID
from bytelang.impl.node.expression import Identifier
from bytelang.impl.node.super import SuperNode
from bytelang.impl.profiles.type import ArrayTypeProfile
from bytelang.impl.profiles.type import PointerTypeProfile
from bytelang.impl.semantizer.common import CommonSemanticContext


class TypeNode(SuperNode[CommonSemanticContext, TypeProfile, 'Type'], ABC):
    """Узел типа"""

    @classmethod
    def parse(cls, parser: Parser) -> LEGACY_Result[TypeNode, Iterable[str]]:
        match parser.tokens.peek().type:
            case TokenType.Star:
                return PointerTypeNode.parse(parser)

            case TokenType.OpenSquare:
                return ArrayTypeNode.parse(parser)

        return PureTypeNode.parse(parser)

    @abstractmethod
    def accept(self, context: CommonSemanticContext) -> LEGACY_Result[TypeProfile, Iterable[str]]:
        pass


@dataclass(frozen=True)
class PureTypeNode(TypeNode, HasExistingID):
    """Чистый тип"""

    def accept(self, context: CommonSemanticContext) -> LEGACY_Result[TypeProfile, Iterable[str]]:
        return context.type_registry.get(self.identifier.id).map(err=lambda e: (e,))

    @classmethod
    def parse(cls, parser: Parser) -> LEGACY_Result[TypeNode, Iterable[str]]:
        """Создать чистый тип на основе идентификатора"""
        return Identifier.parse(parser).map(lambda ok: cls(ok))


@dataclass(frozen=True)
class PointerTypeNode(TypeNode):
    """Тип Указателя"""

    pointer: TypeNode
    """Тип указателя"""

    @classmethod
    def parse(cls, parser: Parser) -> LEGACY_Result[TypeNode, Iterable[str]]:
        parser.tokens.next()
        return TypeNode.parse(parser).map(lambda t: cls(t))

    def accept(self, context: CommonSemanticContext) -> LEGACY_Result[TypeProfile, Iterable[str]]:
        ret = MultiErrorLEGACYResult()
        _type_profile = self.pointer.accept(context)
        return ret.make(lambda: PointerTypeProfile(_type_profile.unwrap()))


@dataclass(frozen=True)
class ArrayTypeNode(TypeNode):
    """Тип Массив"""

    type: TypeNode
    """Тип элементов массива"""
    length: Expression
    """Выражение, определяющее длину массива"""

    @classmethod
    def parse(cls, parser: Parser) -> LEGACY_Result[TypeNode, Iterable[str]]:
        parser.tokens.next()

        ret = MultiErrorLEGACYResult()

        expr = ret.putMulti(Expression.parse(parser))
        ret.putSingle(parser.consume(TokenType.CloseSquare))
        _type = ret.putMulti(TypeNode.parse(parser))

        return ret.make(lambda: cls(_type.unwrap(), expr.unwrap()))

    def accept(self, context: CommonSemanticContext) -> LEGACY_Result[TypeProfile, Iterable[str]]:
        ret = MultiErrorLEGACYResult()

        item_type_profile = ret.putMulti(self.type.accept(context))
        array_length = ret.putMulti(self.length.accept(context))

        return ret.make(lambda: ArrayTypeProfile(item_type_profile.unwrap(), array_length.unwrap().getValue()))


@dataclass(frozen=True)
class Field(SuperNode[CommonSemanticContext, tuple[str, TypeProfile], "Field"], HasExistingID):
    """Узел объявления поля"""

    type: TypeNode
    """Тип поля"""

    def accept(self, context: CommonSemanticContext) -> LEGACY_Result[tuple[str, TypeProfile], Iterable[str]]:
        ret = MultiErrorLEGACYResult()
        type_profile = ret.putMulti(self.type.accept(context))
        return ret.make(lambda: (self.identifier.id, type_profile.unwrap()))

    @classmethod
    def parse(cls, parser: Parser) -> LEGACY_Result[Field, Iterable[str]]:
        """Парсинг токенов в поле"""
        ret = MultiErrorLEGACYResult()

        name = ret.putSingle(Identifier.parse(parser))
        ret.putSingle(parser.consume(TokenType.Colon))
        pure = ret.putMulti(TypeNode.parse(parser))

        return ret.make(lambda: cls(name.unwrap(), pure.unwrap()))
