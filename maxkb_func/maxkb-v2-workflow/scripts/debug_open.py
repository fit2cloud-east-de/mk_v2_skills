#!/usr/bin/env python3
"""Open debug chat session → print chat_id (admin API, system key)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _lib.maxkb_client import MaxKBError, add_common_args, client_from_args, print_json


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    p.add_argument("--app-id", required=True)
    args = p.parse_args()
    c = client_from_args(args)
    try:
        data = c.admin("GET", c.ws(f"application/{args.app_id}/open"))
        print_json(data)
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
