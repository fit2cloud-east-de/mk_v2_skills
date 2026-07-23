#!/usr/bin/env python3
"""Delete tool.

Agent policy: only run when the user explicitly requested deletion and
confirmed; always require --yes + --confirm-name. See AUTH_AND_SAFETY.md §4.

Usage:
  python delete_tool.py --tool-id ID --confirm-name "确切名称" --yes
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _lib.maxkb_client import (
    MaxKBError,
    add_common_args,
    client_from_args,
    print_json,
    require_yes,
)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    p.add_argument("--tool-id", required=True)
    p.add_argument(
        "--confirm-name",
        required=True,
        help="Must exactly match the tool name (secondary confirmation)",
    )
    args = p.parse_args()
    require_yes(args.yes, f"DELETE tool {args.tool_id}")

    c = client_from_args(args)
    try:
        detail = c.data_of(c.admin("GET", c.ws(f"tool/{args.tool_id}")))
        live_name = (detail or {}).get("name") if isinstance(detail, dict) else None
        if live_name is None:
            print(f"[blocked] cannot resolve tool name for {args.tool_id}", file=sys.stderr)
            return 2
        if args.confirm_name != live_name:
            print(
                f"[blocked] --confirm-name mismatch: expected {live_name!r}, got {args.confirm_name!r}",
                file=sys.stderr,
            )
            return 2
        print(
            f"[delete] tool_id={args.tool_id} name={live_name!r} "
            f"tool_type={(detail or {}).get('tool_type')}",
            file=sys.stderr,
        )
        print_json(c.admin("DELETE", c.ws(f"tool/{args.tool_id}")))
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
