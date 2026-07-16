#!/usr/bin/env python3
"""Pylint check for tool code."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _lib.maxkb_client import MaxKBError, add_common_args, client_from_args, print_json


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    p.add_argument("--code", default=None)
    p.add_argument("--code-file", default=None)
    args = p.parse_args()
    if args.code_file:
        code = Path(args.code_file).read_text(encoding="utf-8")
    elif args.code is not None:
        code = args.code
    else:
        p.error("--code or --code-file required")
    c = client_from_args(args)
    try:
        print_json(c.admin("POST", c.ws("tool/pylint"), json_body={"code": code}))
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
