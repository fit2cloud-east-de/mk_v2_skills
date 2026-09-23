#!/usr/bin/env python3
"""Save / update application work_flow (or other editable fields).

Usage:
  python save_workflow.py --app-id ID --workflow-json path.json --yes
  python save_workflow.py --app-id ID --body-json path.json --yes

By default normalizes so the canvas can draw branch anchors and edges:
  - intent-node: 「其他」文案；同步 branch_condition_list；按分支数写入合理 height
  - condition-node: 末条 ELSE；同步 branch_condition_list；按分支写入 height
  - 其它节点：省略 height/width（交给画布测量）
  - 边：清空 pointsList，避免残留控制点把线拉飞
Pass --keep-node-size to retain height/width from JSON (仍会同步 branch_condition_list).
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

# Intent canvas: right "+" Y ≈ top + 397 + index * 41.36 (2.10.x)
_INTENT_FORM_TOP = 397
_INTENT_ROW = 41.36
_INTENT_TAIL = 200  # 输出区 + setHeight(+100) 余量


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
    if t_norm == "ELSE" or t_norm in ("其它", "其他"):
        last["type"] = "ELSE"
        last["conditions"] = []
        last.setdefault("condition", "and")


def _sync_branch_condition_list(
    props: dict[str, Any],
    branch: list[Any],
    *,
    default_height: float = 12,
    height_fn=None,
) -> list[dict[str, Any]]:
    """Right-side '+' anchors are created ONLY from branch_condition_list ids."""
    old = {
        b["id"]: b
        for b in (props.get("branch_condition_list") or [])
        if isinstance(b, dict) and b.get("id")
    }
    new_list: list[dict[str, Any]] = []
    for i, item in enumerate(branch):
        if not isinstance(item, dict):
            continue
        bid = item.get("id")
        if not bid:
            continue
        prev = old.get(bid) or {}
        if height_fn is not None:
            h = height_fn(item, prev)
        else:
            h = prev.get("height", default_height)
            if h is None:
                h = default_height
        new_list.append({"id": bid, "index": i, "height": h})
    props["branch_condition_list"] = new_list
    return new_list


def _intent_node_height(n_branches: int) -> int:
    n = max(int(n_branches), 1)
    return int(_INTENT_FORM_TOP + n * _INTENT_ROW + _INTENT_TAIL)


def _condition_row_height(item: dict[str, Any], prev: dict[str, Any]) -> float:
    if prev.get("height") is not None:
        try:
            return float(prev["height"])
        except (TypeError, ValueError):
            pass
    if item.get("type") == "ELSE":
        return 44.0
    n_cond = len(item.get("conditions") or [])
    return float(max(44, 56 + n_cond * 36))


def _condition_node_height(bcl: list[dict[str, Any]]) -> int:
    # mirrors UI: 75 + sum(height+8) + footer/padding
    total = 75.0
    for item in bcl:
        total += float(item.get("height") or 44) + 8
    return int(total + 120)


def _normalize_edges(wf: dict[str, Any]) -> None:
    """Drop cached bezier points so UI recomputes from anchors."""
    for edge in wf.get("edges") or []:
        if not isinstance(edge, dict):
            continue
        edge["pointsList"] = []
        # keep start/end if present but zeroed — updatePathByAnchor rewrites when anchors exist
        edge["startPoint"] = {"x": 0, "y": 0}
        edge["endPoint"] = {"x": 0, "y": 0}


def normalize_work_flow(wf: dict[str, Any], *, keep_node_size: bool) -> dict[str, Any]:
    """Align AI JSON with UI branch anchors and sizing."""
    nodes = wf.get("nodes") or []
    for node in nodes:
        if not isinstance(node, dict):
            continue
        nid = node.get("id")
        ntype = node.get("type")
        if nid in FIXED_NODE_IDS and ntype and nid != ntype and nid in (
            "base-node",
            "start-node",
            "knowledge-base-node",
        ):
            node["type"] = nid
        props = node.get("properties")
        if not isinstance(props, dict):
            continue

        nd = props.get("node_data")
        branch = nd.get("branch") if isinstance(nd, dict) else None

        if ntype == "intent-node" and isinstance(nd, dict):
            _normalize_intent(nd)
            br = nd.get("branch") if isinstance(nd.get("branch"), list) else []
            _sync_branch_condition_list(props, br, default_height=12)
            if not keep_node_size:
                props.pop("width", None)
                props["height"] = _intent_node_height(len(br))
        elif ntype == "condition-node" and isinstance(nd, dict):
            _normalize_condition(nd)
            br = nd.get("branch") if isinstance(nd.get("branch"), list) else []
            bcl = _sync_branch_condition_list(
                props, br, height_fn=_condition_row_height
            )
            if not keep_node_size:
                props.pop("width", None)
                props["height"] = _condition_node_height(bcl)
        else:
            if not keep_node_size:
                props.pop("height", None)
                props.pop("width", None)

    _normalize_edges(wf)
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
        help="Keep properties.height/width from JSON (branch_condition_list still synced)",
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
