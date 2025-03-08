from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable

from bytelang.abc.parser import Parser
from bytelang.core.profile.type import TypeProfile
from bytelang.core.result import MultipleErrorsResult
from bytelang.core.result import Result
from bytelang.core.tokens import TokenType
from bytelang.impl.node.expression import Expression
from bytelang.impl.node.expression import HasExistingID
from bytelang.impl.node.expression import Identifier
from bytelang.impl.node.super import SuperNode
from bytelang.impl.semantizer.common import CommonSemanticContext


class Type(SuperNode[CommonSemanticContext, TypeProfile, 'Type'], ABC):
    """Узел типа"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Type, Iterable[str]]:
        match parser.tokens.peek().type:
            case TokenType.Star:
                return PointerType.parse(parser)

            case TokenType.OpenSquare:
                return ArrayType.parse(parser)

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

    @classmethod
    def parse(cls, parser: Parser) -> Result[Type, Iterable[str]]:
        parser.tokens.next()
        return Type.parse(parser).map(lambda t: cls(t))

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

    @classmethod
    def parse(cls, parser: Parser) -> Result[Type, Iterable[str]]:
        parser.tokens.next()

        ret = MultipleErrorsResult()

        expr = ret.putMulti(Expression.parse(parser))
        ret.putSingle(parser.consume(TokenType.CloseSquare))
        _type = ret.putMulti(Type.parse(parser))

        return ret.make(lambda: cls(_type.unwrap(), expr.unwrap()))

    def accept(self, context: CommonSemanticContext) -> Result[TypeProfile, Iterable[str]]:
        ret = MultipleErrorsResult()

        element_type_profile = ret.putMulti(self.type.accept(context))
        array_length = ret.putMulti(self.length.accept(context))

        return ret.make(lambda: NotImplemented)


@dataclass(frozen=True)
class Field(SuperNode[CommonSemanticContext, tuple[Identifier, TypeProfile], "Field"], HasExistingID):
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
        pure = ret.putMulti(Type.parse(parser))

        return ret.make(lambda: cls(name.unwrap(), pure.unwrap()))
