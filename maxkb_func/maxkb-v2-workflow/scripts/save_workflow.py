#!/usr/bin/env python3
"""Save / update application work_flow (or other editable fields).

Usage:
  python save_workflow.py --app-id ID --workflow-json path.json --yes
  python save_workflow.py --app-id ID --body-json path.json --yes

By default normalizes UI-locked fields so generated graphs match the canvas:
  - intent-node: force isOther branch content to 「其他」
  - condition-node: ensure trailing ELSE has type ELSE and empty conditions
  - drop properties.height / width (canvas measures like drag-and-drop)
Pass --keep-node-size to retain height/width from JSON.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _lib.maxkb_client import (
    MaxKBError,
    add_common_args,
    client_from_args,
    print_json,
    require_yes,
)

FIXED_NODE_IDS = frozenset(
    {
        "base-node",
        "start-node",
        "knowledge-base-node",
        "tool-base-node",
        "tool-start-node",
        "loop-start-node",
    }
)


def _normalize_intent(nd: dict[str, Any]) -> None:
    branch = nd.get("branch")
    if not isinstance(branch, list):
        return
    others = [b for b in branch if isinstance(b, dict) and b.get("isOther")]
    for b in others:
        b["content"] = "其他"
        b["isOther"] = True
    if not others and branch:
        last = branch[-1]
        if isinstance(last, dict) and last.get("content") in ("其他", "其它", "other", "Other"):
            last["isOther"] = True
            last["content"] = "其他"


def _normalize_condition(nd: dict[str, Any]) -> None:
    branch = nd.get("branch")
    if not isinstance(branch, list) or not branch:
        return
    last = branch[-1]
    if not isinstance(last, dict):
        return
    t = last.get("type")
    t_norm = str(t).strip().upper() if t is not None else ""
    # Only fix trailing ELSE (UI structural label); do not rewrite IF / ELSE IF
    if t_norm == "ELSE" or t_norm in ("其它", "其他"):
        last["type"] = "ELSE"
        last["conditions"] = []
        last.setdefault("condition", "and")


def normalize_work_flow(wf: dict[str, Any], *, keep_node_size: bool) -> dict[str, Any]:
    """Align AI JSON with UI-locked fields and drag-and-drop sizing."""
    nodes = wf.get("nodes") or []
    for node in nodes:
        if not isinstance(node, dict):
            continue
        nid = node.get("id")
        ntype = node.get("type")
        # Keep fixed ids/types consistent when present
        if nid in FIXED_NODE_IDS and ntype and nid != ntype and nid in (
            "base-node",
            "start-node",
            "knowledge-base-node",
        ):
            node["type"] = nid
        props = node.get("properties")
        if not isinstance(props, dict):
            continue
        if not keep_node_size:
            props.pop("height", None)
            props.pop("width", None)
        nd = props.get("node_data")
        if not isinstance(nd, dict):
            continue
        if ntype == "intent-node":
            _normalize_intent(nd)
        elif ntype == "condition-node":
            _normalize_condition(nd)
    return wf


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    p.add_argument("--app-id", required=True)
    p.add_argument("--workflow-json", help="File with {nodes, edges}")
    p.add_argument("--body-json", help="Full PUT body JSON")
    p.add_argument(
        "--keep-node-size",
        action="store_true",
        help="Keep properties.height/width from JSON (default: strip for UI auto-measure)",
    )
    args = p.parse_args()
    require_yes(args.yes, f"update application {args.app_id}")

    if args.body_json:
        body = json.loads(Path(args.body_json).read_text(encoding="utf-8"))
        wf = body.get("work_flow")
        if isinstance(wf, dict):
            body["work_flow"] = normalize_work_flow(wf, keep_node_size=args.keep_node_size)
    elif args.workflow_json:
        wf = json.loads(Path(args.workflow_json).read_text(encoding="utf-8"))
        body = {"work_flow": normalize_work_flow(wf, keep_node_size=args.keep_node_size)}
    else:
        p.error("provide --workflow-json or --body-json")

    c = client_from_args(args)
    try:
        print_json(c.admin("PUT", c.ws(f"application/{args.app_id}"), json_body=body))
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
