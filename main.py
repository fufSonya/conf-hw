
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from config_translator import translate
from config_translator.errors import TranslationError


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Translate educational configuration language to TOML.",
    )
    p.add_argument(
        "-o",
        "--output",
        required=True,
        help="Path to output TOML file",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    src = sys.stdin.read()
    try:
        out = translate(src)
    except TranslationError as e:
        print(str(e), file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 3

    Path(args.output).write_text(out, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
