from __future__ import annotations


class TranslationError(Exception):
    """Base error for translation failures."""


class LexError(TranslationError):
    def __init__(self, message: str, *, line: int, col: int):
        super().__init__(f"{message} (line {line}, col {col})")
        self.line = line
        self.col = col


class ParseError(TranslationError):
    def __init__(self, message: str, *, line: int, col: int):
        super().__init__(f"{message} (line {line}, col {col})")
        self.line = line
        self.col = col


class EvalError(TranslationError):
    pass
