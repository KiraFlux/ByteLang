from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from typing import Sequence

from bytelang.abc.node import Expression
from bytelang.abc.node import Statement
from bytelang.abc.parser import Parser
from bytelang.core.stream import Stream
from bytelang.core.tokens import Operator
from bytelang.core.tokens import Token
from bytelang.core.tokens import TokenType
from rustpy.result import Result


@dataclass(frozen=True)
class Identifier(Expression):
    """Узел Идентификатора"""

    name: str
    """Имя"""

    @classmethod
    def parse(cls, stream: Stream[Token]) -> Result[Identifier, str]:
        """Парсинг токена в узел Идентификатора"""
        token = stream.next()

        if token.type == TokenType.Identifier:
            return Result.ok(cls(token.value))

        return Result.error(f"Ожидался идентификатор, получено: {token}")


@dataclass(frozen=True)
class Literal[T: (int, float, str)](Expression):
    """Узел Литерала"""

    value: T
    """Значение"""

    @classmethod
    def parse(cls, stream: Stream[Token]) -> Result[Literal, str]:
        """Парсинг токена в узел Литерала"""
        token = stream.next()

        if token.type.isLiteral():
            return Result.ok(cls(token.value))

        return Result.error(f"Ожидался литерал, получено: {token}")


@dataclass(frozen=True)
class UnaryOp(Expression):
    """Узел Префиксной Унарной операции"""

    from bytelang.abc.parser import Parser

    op: Operator
    """Оператор"""
    operand: Expression
    """Операнд"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[UnaryOp, Iterable[str]]:
        """Создать узел Префиксной Унарной операции"""

        token = parser.tokens.next()

        if (operator := token.type.asOperator()) is None:
            return Result.error((f"Ожидался оператор, получено: {token}",))

        result = parser.expression()

        if result.isError():
            return Result.error(result.getError())

        return Result.ok(cls(operator, result.unwrap()))


@dataclass(frozen=True)
class BinaryOp(Expression):
    """Узел Бинарной операции"""

    op: Operator
    """Оператор"""
    left: Expression
    """Левый операнд"""
    right: Expression
    """Правый операнд"""


@dataclass(frozen=True)
class Instruction(Statement):
    """Узел вызова инструкции"""

    id: Identifier
    """Идентификатор выражения"""
    args: Sequence[Expression]
    """Аргументы"""

    @classmethod
    def parse(cls, parser: Parser) -> Result[Instruction, Iterable[str]]:
        """Парсинг инструкций"""
        errors = list[str]()

        id_result = Identifier.parse(parser.tokens)

        if id_result.isError():
            errors.append(id_result.getError())

        args = parser.arguments(TokenType.Comma)

        if args.isError():
            errors.extend(args.getError())

        return Result.error(errors) if errors else Result.ok(Instruction(id_result.unwrap(), args.unwrap()))
