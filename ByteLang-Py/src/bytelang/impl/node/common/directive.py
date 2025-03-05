from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from typing import Sequence

from bytelang.abc.node import Directive
from bytelang.abc.node import Expression
from bytelang.abc.parser import Parsable
from bytelang.abc.parser import Parser
from bytelang.core.tokens import TokenType
from bytelang.impl.node.common.expression import Identifier
from bytelang.impl.node.common.type import Field
from rustpy.result import Result


@dataclass(frozen=True)
class ConstDeclareDirective(Directive, Parsable[Directive]):
    """Объявление константного значения"""

    id: Identifier
    """Идентификатор константы"""
    expression: Expression
    """Выражение значения"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        _id = Identifier.parse(parser)

        if _id.isError():
            return Result.error(_id.getError())

        if (r := parser.consume(TokenType.Assignment)).isError():
            return Result.error(r.getError())

        return parser.expression().map(lambda expr: cls(_id.unwrap(), expr))


@dataclass(frozen=True)
class StructDeclareDirective(Directive, Parsable[Directive]):
    """Объявление структурного типа"""

    id: Identifier
    """Идентификатор типа структуры"""
    fields: Sequence[Field]
    """Поля структуры"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Parsable[Directive], Iterable[str]]:
        _id = Identifier.parse(parser)

        if _id.isError():
            return Result.error(_id.getError())

        return parser.braceArguments(lambda: Field.parse(parser), TokenType.OpenFigure, TokenType.CloseFigure).map(lambda f: cls(_id.unwrap(), f))


@dataclass(frozen=True)
class MacroDeclareDirective(Directive, Parsable[Directive]):
    """Узел объявления макроса"""

    id: Identifier
    """Идентификатор макроса"""
    arguments: Sequence[Identifier]
    """Аргументы - идентификаторы"""
    expression: Expression
    """Выражение, в которое развертывается макрос"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Directive, Iterable[str]]:
        _id = Identifier.parse(parser)

        if _id.isError():
            return Result.error(_id.getError())

        args = parser.braceArguments(lambda: Identifier.parse(parser), TokenType.OpenRound, TokenType.CloseRound)

        if args.isError():
            return Result.error(args.getError())

        if (r := parser.consume(TokenType.Arrow)).isError():
            return Result.error((r.getError(),))

        return parser.expression().map(lambda expr: cls(_id.unwrap(), args.unwrap(), expr))
