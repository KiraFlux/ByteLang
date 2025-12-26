from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, final


@final
@dataclass(frozen=True, kw_only=True)
class Token:
    """Token"""

    class Type(Enum):
        """Token Type"""

        # Literal

        literal_string = auto()
        """ "string" """

        literal_number_integer = auto()
        """ -123456 """

        literal_number_integer_character = auto()
        """ 'A' """

        literal_number_integer_hex = auto()
        """ 0x67 """

        literal_number_integer_bin = auto()
        """ 0x1010 """

        literal_number_real = auto()
        """ -123.456 """

        literal_number_real_exp = auto()
        """ -12e-34 """

        # brackets

        bracket_open_round = auto()
        """ ( """

        bracket_close_round = auto()
        """ ) """

        bracket_open_square = auto()
        """ [ """

        bracket_close_square = auto()
        """ ] """

        bracket_open_figure = auto()
        """ { """

        bracket_close_figure = auto()
        """ } """

        # delimiters



    type: Type

    line: int
    col: int

    lexeme: Optional[str] = None
