from __future__ import annotations

from dataclasses import dataclass

from .errors import LexError


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int
    col: int


_SINGLE_CHAR = {
    "{": "LBRACE",
    "}": "RBRACE",
    "(": "LPAREN",
    ")": "RPAREN",
    ",": "COMMA",
    "[": "LBRACKET",
    "]": "RBRACKET",
}


def lex(text: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    line = 1
    col = 1

    def current() -> str:
        return text[i] if i < len(text) else ""

    def advance(n: int = 1) -> None:
        nonlocal i, line, col
        for _ in range(n):
            if i >= len(text):
                return
            ch = text[i]
            i += 1
            if ch == "\n":
                line += 1
                col = 1
            else:
                col += 1

    while i < len(text):
        ch = current()
        if ch.isspace():
            advance()
            continue

        start_line, start_col = line, col

        # Multi-char operators
        if text.startswith("->", i):
            tokens.append(Token("ARROW", "->", start_line, start_col))
            advance(2)
            continue
        if text.startswith("=>", i):
            tokens.append(Token("FATARROW", "=>", start_line, start_col))
            advance(2)
            continue

        # Array prefix "#("
        if text.startswith("#(", i):
            tokens.append(Token("HASHLPAREN", "#(", start_line, start_col))
            advance(2)
            continue

        # Numbers
        if ch.isdigit():
            j = i
            while j < len(text) and text[j].isdigit():
                j += 1
            value = text[i:j]
            tokens.append(Token("NUMBER", value, start_line, start_col))
            advance(j - i)
            continue

        # Names
        if ch == "_" or ch.isalpha():
            j = i + 1
            while j < len(text) and (text[j] == "_" or text[j].isalnum()):
                j += 1
            value = text[i:j]
            tokens.append(Token("IDENT", value, start_line, start_col))
            advance(j - i)
            continue

        # Single char tokens
        if ch in _SINGLE_CHAR:
            tokens.append(Token(_SINGLE_CHAR[ch], ch, start_line, start_col))
            advance()
            continue

        raise LexError(f"Unexpected character {ch!r}", line=start_line, col=start_col)

    tokens.append(Token("EOF", "", line, col))
    return tokens

