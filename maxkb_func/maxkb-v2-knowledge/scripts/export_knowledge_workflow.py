#!/usr/bin/env python3
"""Export a workflow knowledge base ingest graph as .kbwf.

API: GET .../knowledge/{id}/workflow/export

Usage:
  python export_knowledge_workflow.py --knowledge-id KID --out ./export.kbwf
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _lib.maxkb_client import MaxKBError, add_common_args, client_from_args


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    p.add_argument("--knowledge-id", required=True)
    p.add_argument("--out", required=True, help="Output .kbwf path")
    args = p.parse_args()

    out = Path(args.out)
    if out.suffix.lower() != ".kbwf":
        print(f"warning: expected .kbwf suffix, got {out.suffix}", file=sys.stderr)

    c = client_from_args(args)
    try:
        resp = c.admin(
            "GET",
            c.ws(f"knowledge/{args.knowledge_id}/workflow/export"),
            stream=True,
            check_biz_code=False,
        )
        data = resp.content
        if not data:
            print("empty export response", file=sys.stderr)
            return 1
        # Some gateways return JSON error with 200
        if data[:1] in (b"{", b"[") and b'"code"' in data[:200]:
            print(f"export failed (JSON): {data[:500]!r}", file=sys.stderr)
            return 1
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        print(f"wrote {out} ({len(data)} bytes)")
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
