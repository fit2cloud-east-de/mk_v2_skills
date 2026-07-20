#!/usr/bin/env python3
"""Create a folder under APPLICATION | KNOWLEDGE | TOOL.

API: POST /workspace/{WS}/{SOURCE}/folder  (SOURCE must be uppercase)
Body: { name, desc?, parent_id }

parent_id defaults to workspace root id (= workspace UUID).

Permission: may require workspace folder-create / WORKSPACE_MANAGE;
ordinary user keys often get HTTP 403 — then create folder in UI instead.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.maxkb_client import (
    MaxKBError,
    add_common_args,
    client_from_args,
    print_json,
    require_yes,
)

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
    p.add_argument("--name", required=True, help="New folder name")
    p.add_argument("--desc", default="")
    p.add_argument(
        "--parent-id",
        default=None,
        help="Parent folder id; default = workspace root (workspace id)",
    )
    args = p.parse_args()
    require_yes(args.yes, f"create {args.source} folder {args.name!r}")
    c = client_from_args(args)
    body = {
        "name": args.name,
        "desc": args.desc,
        "parent_id": args.parent_id or c.folder_id(),
    }
    try:
        print_json(
            c.admin(
                "POST",
                c.ws(f"{SOURCE_PATH[args.source]}/folder"),
                json_body=body,
            )
        )
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
