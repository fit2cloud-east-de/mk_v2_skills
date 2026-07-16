#!/usr/bin/env python3
"""Knowledge hit test."""
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
    p.add_argument("--query", required=True)
    p.add_argument("--top-number", type=int, default=5)
    p.add_argument("--similarity", type=float, default=0.6)
    p.add_argument("--search-mode", default="embedding", choices=["embedding", "keywords", "blend"])
    args = p.parse_args()
    c = client_from_args(args)
    body = {
        "query_text": args.query,
        "top_number": args.top_number,
        "similarity": args.similarity,
        "search_mode": args.search_mode,
    }
    try:
        print_json(c.admin("POST", c.ws(f"knowledge/{args.knowledge_id}/hit_test"), json_body=body))
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
