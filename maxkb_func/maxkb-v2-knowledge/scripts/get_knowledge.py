#!/usr/bin/env python3
"""Get knowledge base detail (and optionally its ingest workflow).

Usage:
  python get_knowledge.py --knowledge-id KID
  python get_knowledge.py --knowledge-id KID --with-workflow
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _lib.maxkb_client import MaxKBError, add_common_args, client_from_args, print_json


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    p.add_argument("--knowledge-id", required=True)
    p.add_argument(
        "--with-workflow",
        action="store_true",
        help="Also GET .../knowledge/{id}/workflow (ingest graph for workflow KBs)",
    )
    args = p.parse_args()
    c = client_from_args(args)
    try:
        detail = c.admin("GET", c.ws(f"knowledge/{args.knowledge_id}"))
        if not args.with_workflow:
            print_json(detail)
            return 0
        out = {"knowledge": detail}
        try:
            out["workflow"] = c.admin("GET", c.ws(f"knowledge/{args.knowledge_id}/workflow"))
        except MaxKBError as e:
            out["workflow"] = {"error": str(e), "hint": "Only workflow knowledge bases have this endpoint"}
        print_json(out)
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
