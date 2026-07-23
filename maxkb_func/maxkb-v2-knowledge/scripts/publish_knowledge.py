#!/usr/bin/env python3
"""Publish a workflow knowledge base ingest pipeline.

API: PUT .../knowledge/{id}/publish

After editing the ingest graph (import / save_knowledge_workflow), publish
so chat-side retrieval uses the new version.

Usage:
  python publish_knowledge.py --knowledge-id KID --yes
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
    args = p.parse_args()
    require_yes(args.yes, f"publish knowledge workflow {args.knowledge_id}")
    c = client_from_args(args)
    try:
        print_json(c.admin("PUT", c.ws(f"knowledge/{args.knowledge_id}/publish")))
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
