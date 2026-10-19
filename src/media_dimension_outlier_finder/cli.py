from __future__ import annotations

import argparse
import json
import sys
from contextlib import suppress
from pathlib import Path

from .core import analyze, render_json, render_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a deterministic, reviewable report from explicit JSON input."
    )
    parser.add_argument("input", type=Path, help="UTF-8 JSON input file")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        report = analyze(data)
        rendered = render_json(report) if args.format == "json" else render_markdown(report)
        if args.output:
            if args.output.is_symlink():
                raise ValueError("output path is a symbolic link")
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(rendered)
        else:
            try:
                sys.stdout.write(rendered)
                sys.stdout.flush()
            except OSError as exc:
                with suppress(OSError):
                    sys.stdout.close()
                print(f"error: {exc}", file=sys.stderr)
                return 2
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0
