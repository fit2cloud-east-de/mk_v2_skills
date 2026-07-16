#!/usr/bin/env python3
"""List tools."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _lib.maxkb_client import MaxKBError, add_common_args, client_from_args, print_json


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    p.add_argument("--folder-id", default=None, help="Default: workspace root (= workspace id)")
    p.add_argument("--name", default=None)
    p.add_argument("--tool-type", default=None)
    p.add_argument("--scope", default="WORKSPACE", help="Required by /tool/tool_list")
    p.add_argument("--all-list", action="store_true", help="Use /tool/tool_list")
    args = p.parse_args()
    c = client_from_args(args)
    params = {"folder_id": args.folder_id or c.folder_id()}
    if args.name:
        params["name"] = args.name
    if args.tool_type:
        params["tool_type"] = args.tool_type
    if args.all_list:
        params["scope"] = args.scope
        path = c.ws("tool/tool_list")
    else:
        path = c.ws("tool")
    try:
        print_json(c.admin("GET", path, params=params))
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
