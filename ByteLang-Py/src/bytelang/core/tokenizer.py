import re
from dataclasses import dataclass
from typing import ClassVar
from typing import Sequence
from typing import TextIO

from bytelang.core.key_word import Keyword
from bytelang.core.stream import CollectionOutputStream
from bytelang.core.tokens import Token
from bytelang.core.tokens import TokenType
from rustpy.option import none
from rustpy.option import some
from rustpy.result import Result
from rustpy.result import err
from rustpy.result import ok


@dataclass(frozen=True)
class Tokenizer:
    """Лексический анализатор"""

    keywords: Sequence[Keyword]
    """Ключевые слова"""

    def run(self, source: TextIO) -> Result[CollectionOutputStream[Token], CollectionOutputStream[str]]:
        """Преобразовать исходный код в поток токенов или поток ошибок"""

        tokens = list[Token]()
        errors = list[str]()

        for line_index, line_source in enumerate(source):
            column = 0
            line_len = len(line_source)

            while column < line_len:
                if line_source[column].isspace():
                    column += 1
                    continue

                matched = False

                for token_type, pattern in self._patterns:
                    if match := pattern.match(line_source, column):
                        match: re.Match
                        lexeme = match.group(0)
                        end_pos = match.end()

                        if token_type == TokenType.Comment:
                            column = end_pos
                            matched = True
                            break

                        if token_type == TokenType.Identifier:
                            if any(kw.id == lexeme for kw in self.keywords):
                                token_type = TokenType.Keyword

                        tokens.append(self._makeToken(token_type, lexeme))

                        column = end_pos
                        matched = True
                        break

                if not matched:
                    errors.append(self._makeErrorMessage(line_source, line_index + 1, column))
                    column += 1

        return (
            err(CollectionOutputStream(errors))
            if errors else
            ok(CollectionOutputStream(tokens))
        )

    def _makeErrorMessage(self, line_source: str, line_number: int, column: int):
        snippet = line_source[column:column + self._snippet_length]

        if len(snippet) > self._snippet_length:
            snippet = f"{snippet[:self._snippet_length]}..."

        return f"Строка {line_number}, позиция {column}: неизвестный токен '{snippet}'"

    @classmethod
    def _makeToken(cls, token_type: TokenType, lexeme: str) -> Token:
        return Token(
            type=token_type,
            lexeme=(
                some(lexeme)
                if cls._isTokenHasLexeme(token_type) else
                none()
            )
        )

    @classmethod
    def _isTokenHasLexeme(cls, token_type: TokenType) -> bool:
        return token_type in cls._token_type_with_lexeme

    @staticmethod
    def _get_token_spec() -> Sequence[tuple[TokenType, str]]:
        return (
            (TokenType.Comment, r'#.*'),
            (TokenType.String, r'\"(?:[^\"\\]|\\.)*\"'),
            (TokenType.Character, r'\'(?:[^\'\\]|\\.)\''),
            (TokenType.Real, r'-?\d+\.\d+([eE][-+]?\d+)?'),
            (TokenType.Integer, r'-?\d+'),
            (TokenType.Arrow, r'->'),
            (TokenType.Assign, r'='),
            (TokenType.Colon, r':'),
            (TokenType.StatementEnd, r';'),
            (TokenType.Comma, r','),
            (TokenType.Plus, r'\+'),
            (TokenType.Dash, r'-'),
            (TokenType.Slash, r'/'),
            (TokenType.Star, r'\*'),
            (TokenType.Dot, r'\.'),
            (TokenType.Cast, r'as'),
            (TokenType.OpenRound, r'\('),
            (TokenType.CloseRound, r'\)'),
            (TokenType.OpenFigure, r'\{'),
            (TokenType.CloseFigure, r'\}'),
            (TokenType.OpenSquare, r'\['),
            (TokenType.CloseSquare, r'\]'),
            (TokenType.OpenAngle, r'<'),
            (TokenType.CloseAngle, r'>'),
            (TokenType.Identifier, r'[a-zA-Z_][a-zA-Z0-9_]*'),
        )

    @staticmethod
    def _compile_patterns(spec: Sequence) -> Sequence[tuple[TokenType, re.Pattern]]:
        return tuple(
            (token_type, re.compile(pattern))
            for token_type, pattern in spec
        )

    _snippet_length: ClassVar = 32
    _patterns: ClassVar = _compile_patterns(_get_token_spec())

    _token_type_with_lexeme: ClassVar = {
        TokenType.Comment,
        TokenType.String,
        TokenType.Character,
        TokenType.Real,
        TokenType.Integer,
        TokenType.Identifier,
        TokenType.Keyword
    }
