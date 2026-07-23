#!/usr/bin/env python3
"""Save / update the ingest workflow graph of a workflow knowledge base.

API: PUT .../knowledge/{id}/workflow
Body: { "work_flow": { "nodes": [...], "edges": [...] } }

Usage:
  python save_knowledge_workflow.py --knowledge-id KID --workflow-json path.json --yes
  python save_knowledge_workflow.py --knowledge-id KID --body-json path.json --yes
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
    p.add_argument("--workflow-json", help="File with {nodes, edges} → wrapped as work_flow")
    p.add_argument("--body-json", help="Full PUT body (must include work_flow)")
    args = p.parse_args()
    require_yes(args.yes, f"update knowledge workflow {args.knowledge_id}")

    if args.body_json:
        body = json.loads(Path(args.body_json).read_text(encoding="utf-8"))
    elif args.workflow_json:
        wf = json.loads(Path(args.workflow_json).read_text(encoding="utf-8"))
        if isinstance(wf, dict) and "work_flow" in wf:
            body = wf
        else:
            body = {"work_flow": wf}
    else:
        p.error("provide --workflow-json or --body-json")

    if not isinstance(body, dict) or not body.get("work_flow"):
        print("body must contain non-empty work_flow", file=sys.stderr)
        return 1

    c = client_from_args(args)
    try:
        print_json(
            c.admin("PUT", c.ws(f"knowledge/{args.knowledge_id}/workflow"), json_body=body)
        )
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
