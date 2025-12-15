from __future__ import annotations

from dataclasses import dataclass

from .errors import EvalError
from .parser import Array, ConstDecl, ConstRef, Dict, Expr, Number, Program


Value = int | list["Value"] | dict[str, "Value"]


def eval_program(program: Program) -> Value:
    env: dict[str, Value] = {}
    for decl in program.decls:
        env[decl.name] = eval_expr(decl.expr, env)
    return eval_expr(program.result, env)


def eval_expr(expr: Expr, env: dict[str, Value]) -> Value:
    if isinstance(expr, Number):
        return expr.value
    if isinstance(expr, Array):
        return [eval_expr(x, env) for x in expr.items]
    if isinstance(expr, Dict):
        out: dict[str, Value] = {}
        for k, v in expr.items:
            out[k] = eval_expr(v, env)
        return out
    if isinstance(expr, ConstRef):
        if expr.name not in env:
            raise EvalError(f"Undefined constant [{expr.name}]")
        return env[expr.name]
    raise EvalError(f"Unsupported expression: {expr!r}")

