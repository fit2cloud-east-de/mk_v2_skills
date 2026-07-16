#!/usr/bin/env python3
"""List workspaces for current API key (name + id)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib.maxkb_client import MaxKBClient, MaxKBError, add_common_args, print_json


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    args = p.parse_args()
    # skip auto-resolve; we only list
    try:
        c = MaxKBClient(host=args.host, api_key=args.api_key, workspace="default", resolve_workspace=False)
        try:
            data = c.data_of(c.admin("GET", "/workspace/by_user"))
        except MaxKBError:
            data = c.data_of(c.admin("GET", "/user/profile")).get("workspace_list")
        print_json(data)
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
