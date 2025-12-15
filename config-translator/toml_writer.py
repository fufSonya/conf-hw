from __future__ import annotations

from .errors import EvalError
from .eval import Value


def dumps(value: Value) -> str:
    if isinstance(value, dict):
        lines: list[str] = []
        _write_table(lines, [], value)
        return "\n".join(lines).rstrip() + "\n"
    return f"value = {_format_value(value)}\n"


def _write_table(lines: list[str], path: list[str], table: dict[str, Value]) -> None:
    scalar_items: list[tuple[str, Value]] = []
    dict_items: list[tuple[str, dict[str, Value]]] = []
    aot_items: list[tuple[str, list[dict[str, Value]]]] = []

    for k, v in table.items():
        if isinstance(v, dict):
            dict_items.append((k, v))
        elif isinstance(v, list) and _is_array_of_tables(v):
            aot_items.append((k, v))  # type: ignore[arg-type]
        else:
            scalar_items.append((k, v))

    for k, v in scalar_items:
        lines.append(f"{k} = {_format_value(v)}")

    for k, subt in dict_items:
        full = ".".join(path + [k])
        if lines and lines[-1] != "":
            lines.append("")
        lines.append(f"[{full}]")
        _write_table(lines, path + [k], subt)

    for k, aot in aot_items:
        full = ".".join(path + [k])
        for idx, elem in enumerate(aot):
            if lines and lines[-1] != "":
                lines.append("")
            lines.append(f"[[{full}]]")
            _write_table(lines, path + [k], elem)


def _is_array_of_tables(v: list[Value]) -> bool:
    return len(v) > 0 and all(isinstance(x, dict) for x in v)


def _format_value(v: Value) -> str:
    if isinstance(v, int):
        return str(v)
    if isinstance(v, dict):
        raise EvalError("Nested dictionaries must appear as tables, not inline values")
    if isinstance(v, list):
        _assert_toml_array_is_valid(v)
        return "[" + ", ".join(_format_value(x) for x in v) + "]"
    raise EvalError(f"Unsupported TOML value: {v!r}")


def _type_tag(v: Value) -> str:
    if isinstance(v, int):
        return "int"
    if isinstance(v, dict):
        return "dict"
    if isinstance(v, list):
        return "list"
    return "unknown"


def _assert_toml_array_is_valid(items: list[Value]) -> None:
    if not items:
        return
    first_tag = _type_tag(items[0])
    for x in items[1:]:
        if _type_tag(x) != first_tag:
            raise EvalError("TOML arrays must be homogeneous (same element types)")
    if first_tag == "dict":
        raise EvalError("Array of dictionaries must be written as array-of-tables")
