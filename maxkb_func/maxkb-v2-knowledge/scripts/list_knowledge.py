#!/usr/bin/env python3
"""List knowledge bases."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _lib.maxkb_client import MaxKBError, add_common_args, client_from_args, print_json


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    p.add_argument("--name", default=None)
    p.add_argument("--folder-id", default=None)
    p.add_argument("--page", type=int, default=0)
    p.add_argument("--size", type=int, default=20)
    args = p.parse_args()
    c = client_from_args(args)
    params = {}
    if args.name:
        params["name"] = args.name
    if args.folder_id:
        params["folder_id"] = args.folder_id
    try:
        if args.page > 0:
            data = c.admin("GET", c.ws(f"knowledge/{args.page}/{args.size}"), params=params or None)
        else:
            data = c.admin("GET", c.ws("knowledge"), params=params or None)
        print_json(data)
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
