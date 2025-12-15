from __future__ import annotations

from dataclasses import dataclass

from .errors import ParseError
from .lexer import Token


@dataclass(frozen=True)
class Number:
    value: int


@dataclass(frozen=True)
class Array:
    items: list["Expr"]


@dataclass(frozen=True)
class Dict:
    items: list[tuple[str, "Expr"]]


@dataclass(frozen=True)
class ConstRef:
    name: str


Expr = Number | Array | Dict | ConstRef


@dataclass(frozen=True)
class ConstDecl:
    name: str
    expr: Expr


@dataclass(frozen=True)
class Program:
    decls: list[ConstDecl]
    result: Expr


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.i = 0

    def peek(self) -> Token:
        return self.tokens[self.i]

    def at(self, kind: str) -> bool:
        return self.peek().kind == kind

    def consume(self, kind: str) -> Token:
        tok = self.peek()
        if tok.kind != kind:
            raise ParseError(
                f"Expected {kind}, got {tok.kind}",
                line=tok.line,
                col=tok.col,
            )
        self.i += 1
        return tok

    def maybe(self, kind: str) -> Token | None:
        if self.at(kind):
            return self.consume(kind)
        return None

    def parse_program(self) -> Program:
        decls: list[ConstDecl] = []
        result: Expr | None = None

        while not self.at("EOF"):
            expr = self.parse_value()
            if self.maybe("ARROW"):
                name_tok = self.consume("IDENT")
                decls.append(ConstDecl(name=name_tok.value, expr=expr))
                continue

            result = expr
            if not self.at("EOF"):
                tok = self.peek()
                raise ParseError(
                    "Unexpected tokens after final expression",
                    line=tok.line,
                    col=tok.col,
                )
            break

        if result is None:
            tok = self.peek()
            raise ParseError("Expected expression", line=tok.line, col=tok.col)
        self.consume("EOF")
        return Program(decls=decls, result=result)

    def parse_value(self) -> Expr:
        tok = self.peek()
        if tok.kind == "NUMBER":
            self.consume("NUMBER")
            return Number(int(tok.value))
        if tok.kind == "HASHLPAREN":
            return self.parse_array()
        if tok.kind == "LBRACE":
            return self.parse_dict()
        if tok.kind == "LBRACKET":
            return self.parse_const_ref()

        raise ParseError(
            f"Expected value, got {tok.kind}",
            line=tok.line,
            col=tok.col,
        )

    def parse_array(self) -> Array:
        self.consume("HASHLPAREN")
        items: list[Expr] = []
        if not self.at("RPAREN"):
            items.append(self.parse_value())
            while self.maybe("COMMA"):
                if self.at("RPAREN"):
                    break
                items.append(self.parse_value())
        self.consume("RPAREN")
        return Array(items)

    def parse_dict(self) -> Dict:
        self.consume("LBRACE")
        items: list[tuple[str, Expr]] = []
        if not self.at("RBRACE"):
            items.append(self.parse_pair())
            while self.maybe("COMMA"):
                if self.at("RBRACE"):
                    break
                items.append(self.parse_pair())
        self.consume("RBRACE")
        return Dict(items)

    def parse_pair(self) -> tuple[str, Expr]:
        key = self.consume("IDENT").value
        self.consume("FATARROW")
        value = self.parse_value()
        return key, value

    def parse_const_ref(self) -> ConstRef:
        lb = self.consume("LBRACKET")
        name = self.consume("IDENT").value
        if not self.at("RBRACKET"):
            tok = self.peek()
            raise ParseError("Expected closing ']'", line=tok.line, col=tok.col)
        self.consume("RBRACKET")
        return ConstRef(name=name)


def parse(tokens: list[Token]) -> Program:
    return Parser(tokens).parse_program()
