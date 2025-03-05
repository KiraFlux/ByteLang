from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable
from typing import Sequence

from bytelang.abc.node import Directive
from bytelang.abc.node import Expression
from bytelang.abc.parser import Parser
from bytelang.core.tokens import TokenType
from bytelang.impl.node.common.type import Field
from bytelang.impl.node.common.expression import Identifier
from rustpy.result import Result


class ParsableDirective(Directive, ABC):
    """Директива, поддерживающая парсинг из токенов"""

    @classmethod
    @abstractmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        """Преобразовать токены в конкретную директиву"""


@dataclass(frozen=True)
class ConstDeclareDirective(ParsableDirective):
    """Объявление константного значения"""

    id: Identifier
    """Идентификатор константы"""
    expression: Expression
    """Выражение значения"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        _id = Identifier.parse(parser.tokens)

        if _id.isError():
            return Result.error(_id.getError())

        if (r := parser.consume(TokenType.Assignment)).isError():
            return Result.error(r.getError())

        result = parser.expression()

        if result.isError():
            return Result.error(result.getError())

        return Result.ok(cls(_id.unwrap(), result.unwrap()))


@dataclass(frozen=True)
class StructDeclareDirective(ParsableDirective):
    """Объявление структурного типа"""

    id: Identifier
    """Идентификатор типа структуры"""
    fields: Sequence[Field]
    """Поля структуры"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        _id = Identifier.parse(parser.tokens)

        if _id.isError():
            return Result.error((_id.getError(),))

        fields = parser.braceArguments(lambda: Field.parse(parser.tokens).map(lambda e: (e,)), TokenType.OpenFigure, TokenType.CloseFigure)

        if fields.isError():
            return Result.error(fields.getError())

        return Result.ok(cls(_id.unwrap(), fields.unwrap()))


@dataclass(frozen=True)
class MacroDeclareDirective(ParsableDirective):
    """Узел объявления макроса"""

    id: Identifier
    """Идентификатор макроса"""
    arguments: Sequence[Identifier]
    """Аргументы - идентификаторы"""
    expression: Expression
    """Выражение, в которое развертывается макрос"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        # .macro foo(a, b, c) -> (a + b) * c
        _id = Identifier.parse(parser.tokens)

        if _id.isError():
            return Result.error((_id.getError(),))

        args = parser.braceArguments(lambda: Identifier.parse(parser.tokens).map(lambda e: (e,)), TokenType.OpenRound, TokenType.CloseRound)

        if args.isError():
            return Result.error(args.getError())

        if (r := parser.consume(TokenType.Arrow)).isError():
            return Result.error((r.getError(),))

        expr = parser.expression()

        if expr.isError():
            return Result.error(expr.getError())

        return Result.ok(cls(_id.unwrap(), args.unwrap(), expr.unwrap()))
