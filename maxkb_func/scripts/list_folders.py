#!/usr/bin/env python3
"""List folders for application | knowledge | tool in the workspace.

API: GET /workspace/{WS}/{source}/folder
source path: application | knowledge | tool
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.maxkb_client import MaxKBError, add_common_args, client_from_args, print_json

# EE folder API uses uppercase source segments (APPLICATION|KNOWLEDGE|TOOL)
SOURCE_PATH = {
    "APPLICATION": "APPLICATION",
    "KNOWLEDGE": "KNOWLEDGE",
    "TOOL": "TOOL",
}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    p.add_argument(
        "--source",
        required=True,
        choices=tuple(SOURCE_PATH.keys()),
        help="APPLICATION | KNOWLEDGE | TOOL",
    )
    p.add_argument("--name", default=None, help="Optional name filter")
    args = p.parse_args()
    c = client_from_args(args)
    params = {"name": args.name} if args.name else None
    try:
        print_json(
            c.admin("GET", c.ws(f"{SOURCE_PATH[args.source]}/folder"), params=params)
        )
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
