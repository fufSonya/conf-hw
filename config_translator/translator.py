from __future__ import annotations

from .eval import eval_program
from .lexer import lex
from .parser import parse
from .toml_writer import dumps


def translate(text: str) -> str:
    """
    Translate educational configuration language source into TOML text.

    Input: source string (may include whitespace/newlines).
    Output: TOML document string (always ends with newline).
    """
    tokens = lex(text)
    program = parse(tokens)
    value = eval_program(program)
    return dumps(value)

