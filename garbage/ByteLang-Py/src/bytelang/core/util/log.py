from __future__ import annotations

from dataclasses import dataclass
from functools import wraps
from os import PathLike
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class Logger:
    _key: str

    @classmethod
    def fromFile(cls, path: PathLike[str]) -> Logger:
        return cls(Path(path).stem)

    def sub(self, key: str) -> Logger:
        return Logger(self._makeSubKey(key))

    def attach[T, R](self, *, show_args: bool = False) -> Callable[[T], R]:
        def _l(f: Callable[[T], R]) -> Callable[[T], R]:
            @wraps(f)
            def _w(*args: T) -> R:
                r = f(*args)

                args = f"{args}" if show_args else "(...)"

                self._sendMessage(self._formatMessage(f, args, r))
                return r

            return _w

        return _l

    def _makeSubKey(self, sub: str) -> str:
        return f"{self._key}::{sub}"

    def _formatMessage[T, R](self, f: Callable[[T], R], args: str, ret: R) -> str:
        return f"[ {self._key} ] : {f.__name__}{args} -> {ret}"

    @staticmethod
    def _sendMessage(message: str) -> None:
        print(message)


def _test():
    _logger = Logger("Test")

    @_logger.sub("show").attach(show_args=True)
    def foo(a: int, b: int) -> int:
        return a + b

    @_logger.sub("hide").attach(show_args=False)
    def bar(a: int, b: int) -> int:
        return a + b

    foo(1, 5)
    bar(2, 3)


if __name__ == '__main__':
    _test()
