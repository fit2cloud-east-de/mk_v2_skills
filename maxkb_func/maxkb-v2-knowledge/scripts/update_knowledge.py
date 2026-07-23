#!/usr/bin/env python3
"""Update knowledge base metadata (name/desc/folder/embedding/…).

API: PUT .../knowledge/{id}

Does NOT replace the ingest workflow graph — use save_knowledge_workflow.py
or import_knowledge_workflow.py for that.

Usage:
  python update_knowledge.py --knowledge-id KID --name "新名称" --yes
  python update_knowledge.py --knowledge-id KID --body-json ./patch.json --yes
"""
from __future__ import annotations

import argparse
import json
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
    p.add_argument("--name", default=None)
    p.add_argument("--desc", default=None)
    p.add_argument("--folder-id", default=None)
    p.add_argument("--embedding-model-id", default=None)
    p.add_argument("--body-json", help="Full PUT body JSON (overrides field flags)")
    args = p.parse_args()
    require_yes(args.yes, f"update knowledge {args.knowledge_id}")

    if args.body_json:
        body = json.loads(Path(args.body_json).read_text(encoding="utf-8"))
    else:
        body = {}
        if args.name is not None:
            body["name"] = args.name
        if args.desc is not None:
            body["desc"] = args.desc
        if args.folder_id is not None:
            body["folder_id"] = args.folder_id
        if args.embedding_model_id is not None:
            body["embedding_model_id"] = args.embedding_model_id
        if not body:
            p.error("provide at least one of --name/--desc/--folder-id/--embedding-model-id or --body-json")

    c = client_from_args(args)
    try:
        print_json(c.admin("PUT", c.ws(f"knowledge/{args.knowledge_id}"), json_body=body))
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
