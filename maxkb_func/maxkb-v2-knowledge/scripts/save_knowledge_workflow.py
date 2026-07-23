#!/usr/bin/env python3
"""Save / update the ingest workflow graph of a workflow knowledge base.

API: PUT .../knowledge/{id}/workflow
Body: { "work_flow": { "nodes": [...], "edges": [...] } }

Prevents UI publish errors by default:
  - auto-fix id=knowledge-base-node if missing (「基本信息节点必填」)
  - block save if no data-source (「开始节点必填」)
  - block save if no knowledge-write-node

Usage:
  python save_knowledge_workflow.py --knowledge-id KID --workflow-json path.json --yes
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _lib.knowledge_workflow_graph import ensure_publish_shape, precheck_workflow
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
    p.add_argument(
        "--no-fix-base",
        action="store_true",
        help="Do not auto-inject knowledge-base-node (default: inject if missing)",
    )
    p.add_argument(
        "--skip-precheck",
        action="store_true",
        help="Skip publish-shape precheck (not recommended)",
    )
    args = p.parse_args()
    require_yes(args.yes, f"update knowledge workflow {args.knowledge_id}")

    if args.body_json:
        body = json.loads(Path(args.body_json).read_text(encoding="utf-8-sig"))
    elif args.workflow_json:
        wf = json.loads(Path(args.workflow_json).read_text(encoding="utf-8-sig"))
        if isinstance(wf, dict) and "work_flow" in wf:
            body = wf
        else:
            body = {"work_flow": wf}
    else:
        p.error("provide --workflow-json or --body-json")

    if not isinstance(body, dict) or not body.get("work_flow"):
        print("body must contain non-empty work_flow", file=sys.stderr)
        return 1

    work_flow = body["work_flow"]
    if not isinstance(work_flow, dict):
        print("work_flow must be an object", file=sys.stderr)
        return 1

    work_flow, notes = ensure_publish_shape(
        work_flow, fix_base=not args.no_fix_base
    )
    for n in notes:
        print(f"[fix] {n}", file=sys.stderr)
    body["work_flow"] = work_flow

    if not args.skip_precheck:
        problems = precheck_workflow(work_flow)
        if problems:
            print("[blocked] 保存前校验失败（与界面发布一致），可避免「基本信息/开始节点必填」：", file=sys.stderr)
            for msg in problems:
                print(f"  - {msg}", file=sys.stderr)
            print(
                "补齐数据源与写入节点后再保存；或 create_knowledge --kind workflow 使用默认骨架。",
                file=sys.stderr,
            )
            return 2

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
