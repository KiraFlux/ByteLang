from abc import ABC
from dataclasses import dataclass
from typing import Final
from typing import Sequence

from bytelang.core.tokens import Operator


class Node(ABC):
    """Узел AST"""

    _debug_display_indent: Final[int] = 4
    """Отступ дочерних узлов"""


class Expression(Node):
    """Узел Выражения"""


@dataclass(frozen=True)
class Identifier(Expression):
    """Узел Идентификатора"""

    name: str
    """Имя"""


@dataclass(frozen=True)
class Literal[T: (int, float, str)](Expression):
    """Узел Литерала"""

    value: T
    """Значение"""


@dataclass(frozen=True)
class UnaryOp(Expression):
    """Узел Унарной операции"""

    op: Operator
    """Оператор"""
    operand: Expression
    """Операнд"""


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
class Statement(Node):
    """Узел Statement"""

    id: Identifier
    """Идентификатор вызываемого"""
    args: Sequence[Expression]
    """Аргументы"""


class Instruction(Statement):
    """Узел вызова инструкции"""


class Directive(Statement):
    """Узел Директивы"""


@dataclass(frozen=True)
class Program(Node):
    """Узел программы"""

    statements: Sequence[Statement]
    """Statements"""


def _test():
    n = Program(
        (
            Directive(Identifier("env"), (Literal[str]("esp32"),)),
            Instruction(Identifier("go"), (BinaryOp(Operator.Plus, Literal(5), Identifier("x")),)),
        )
    )

    print(n)


if __name__ == '__main__':
    _test()
