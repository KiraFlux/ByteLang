from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from bytelang.abc.node import Directive
from bytelang.abc.node import Expression
from bytelang.abc.parser import Parsable
from bytelang.abc.parser import Parser
from bytelang.core.tokens import TokenType
from bytelang.impl.node.expression import Identifier
from bytelang.impl.node.type import Field
from rustpy.result import MultipleErrorsResult
from rustpy.result import Result


@dataclass(frozen=True)
class ConstDefineDirective(Directive, Parsable[Directive]):
    """Узел определения константного значения"""

    id: Identifier
    """Идентификатор константы"""
    expression: Expression
    """Выражение значения"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        ret = MultipleErrorsResult()

        _id = ret.putSingle(Identifier.parse(parser))
        ret.putSingle(parser.consume(TokenType.Assignment))
        expr = ret.putMulti(parser.expression())

        return ret.make(lambda: cls(_id.unwrap(), expr.unwrap()))


@dataclass(frozen=True)
class StructDefineDirective(Directive, Parsable[Directive]):
    """Узел определения структурного типа"""

    id: Identifier
    """Идентификатор типа структуры"""
    fields: Iterable[Field]
    """Поля структуры"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Parsable[Directive], Iterable[str]]:
        ret = MultipleErrorsResult()

        _id = ret.putSingle(Identifier.parse(parser))
        fields = ret.putMulti(parser.braceArguments(lambda: Field.parse(parser), TokenType.OpenFigure, TokenType.CloseFigure))

        return ret.make(lambda: cls(_id.unwrap(), fields.unwrap()))


@dataclass(frozen=True)
class MacroDefineDirective(Directive, Parsable[Directive]):
    """Узел определения макроса"""

    id: Identifier
    """Идентификатор макроса"""
    arguments: Iterable[Identifier]
    """Аргументы - идентификаторы"""
    expression: Expression
    """Выражение, в которое развертывается макрос"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        ret = MultipleErrorsResult()

        _id = ret.putSingle(Identifier.parse(parser))
        args = ret.putMulti(parser.braceArguments(lambda: Identifier.parse(parser), TokenType.OpenRound, TokenType.CloseRound))
        ret.putSingle(parser.consume(TokenType.Arrow))
        expr = ret.putMulti(parser.expression())

        return ret.make(lambda: cls(_id.unwrap(), args.unwrap(), expr.unwrap()))


@dataclass(frozen=True)
class InstructionDefineDirective(Directive, Parsable[Directive]):
    """Узел определения структуры"""

    id: Identifier
    """Идентификатор инструкции"""
    args: Iterable[Field]
    """Аргументы"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        ret = MultipleErrorsResult()

        _id = ret.putSingle(Identifier.parse(parser))
        args = ret.putMulti(parser.braceArguments(lambda: Field.parse(parser), TokenType.OpenRound, TokenType.CloseRound))

        return ret.make(lambda: cls(_id.unwrap(), args.unwrap()))


@dataclass(frozen=True)
class EnvSelectDirective(Directive, Parsable[Directive]):
    """Директива выбора окружения"""

    env: Identifier
    """Идентификатор окружения"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        return Identifier.parse(parser).map(lambda ok: cls(ok))


@dataclass(frozen=True)
class MarkDefineDirective(Directive, Parsable[Directive]):
    """Узел определения метки"""

    mark: Identifier
    """Имя метки"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        return Identifier.parse(parser).map(lambda ok: cls(ok))
