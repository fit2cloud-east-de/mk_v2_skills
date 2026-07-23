#!/usr/bin/env python3
"""Delete knowledge base (base / web / workflow).

Agent policy (AUTH_AND_SAFETY.md §4):
  1. User must explicitly request deletion of this resource.
  2. Agent lists type/name/id and asks for reply「确认删除」.
  3. Then run with --confirm-name matching the live KB name + --yes.

Usage:
  python delete_knowledge.py --knowledge-id KID --confirm-name "确切名称" --yes
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
    p.add_argument("--knowledge-id", required=True)
    p.add_argument(
        "--confirm-name",
        required=True,
        help="Must exactly match the knowledge base name (secondary confirmation)",
    )
    args = p.parse_args()
    require_yes(args.yes, f"DELETE knowledge {args.knowledge_id}")

    c = client_from_args(args)
    try:
        detail = c.data_of(c.admin("GET", c.ws(f"knowledge/{args.knowledge_id}")))
        live_name = (detail or {}).get("name") if isinstance(detail, dict) else None
        if live_name is None:
            print(f"[blocked] cannot resolve knowledge name for {args.knowledge_id}", file=sys.stderr)
            return 2
        if args.confirm_name != live_name:
            print(
                f"[blocked] --confirm-name mismatch: expected {live_name!r}, got {args.confirm_name!r}\n"
                "Re-confirm the exact name with the user, then retry.",
                file=sys.stderr,
            )
            return 2
        print(
            f"[delete] knowledge_id={args.knowledge_id} name={live_name!r} "
            f"type={(detail or {}).get('type')}",
            file=sys.stderr,
        )
        print_json(c.admin("DELETE", c.ws(f"knowledge/{args.knowledge_id}")))
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
