#!/usr/bin/env python3
"""Debug (dry-run ingest) a workflow knowledge base, then poll until done.

API:
  POST .../knowledge/{id}/debug
  GET  .../knowledge/{id}/action/{action_id}

Body shape (same as UI DebugDrawer):
  {
    "data_source": { "node_id": "<data-source node id>", ...form fields },
    "knowledge_base": { ...optional user_input fields }
  }

Local file path:
  1) Upload via POST /oss/file (source_type=KNOWLEDGE, source_id=knowledge_id)
  2) data_source.file_list = [{ name, file_id, status: "success" }]

Web path:
  data_source.source_url + optional selector

Usage:
  python debug_knowledge_workflow.py --knowledge-id KID --file ./sample.md --yes
  python debug_knowledge_workflow.py --knowledge-id KID --source-url https://example.com --yes
  python debug_knowledge_workflow.py --knowledge-id KID --body-json ./debug.json --yes
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _lib.maxkb_client import (
    MaxKBError,
    add_common_args,
    client_from_args,
    print_json,
    require_yes,
)

TERMINAL = {"SUCCESS", "FAILURE", "REVOKED", "REVOKE"}


def _pick_source_node(wf: dict, prefer_type: str | None, explicit_id: str | None) -> dict:
    nodes = (wf or {}).get("nodes") or []
    sources = [n for n in nodes if (n.get("properties") or {}).get("kind") == "data-source"]
    if not sources:
        # fallback: type name contains data-source
        sources = [n for n in nodes if str(n.get("type", "")).startswith("data-source")]
    if explicit_id:
        for n in sources:
            if n.get("id") == explicit_id:
                return n
        raise SystemExit(f"source node_id not found among data-source nodes: {explicit_id}")
    if prefer_type:
        for n in sources:
            if n.get("type") == prefer_type:
                return n
    if not sources:
        raise SystemExit("no data-source node in knowledge workflow; cannot debug")
    return sources[0]


def _upload_file(c, knowledge_id: str, path: Path) -> dict:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    with path.open("rb") as f:
        files = {"file": (path.name, f, mime)}
        data = {"source_id": knowledge_id, "source_type": "KNOWLEDGE"}
        payload = c.admin("POST", "/oss/file", files=files, data=data)
    raw = c.data_of(payload)
    # UI expects "./oss/file/{uuid}" → last segment = file_id
    if isinstance(raw, str):
        file_id = raw.rstrip("/").split("/")[-1]
    elif isinstance(raw, dict):
        file_id = raw.get("id") or raw.get("file_id") or str(raw)
    else:
        raise SystemExit(f"unexpected upload response: {raw!r}")
    return {"name": path.name, "file_id": file_id, "status": "success", "size": path.stat().st_size}


def _poll(c, knowledge_id: str, action_id: str, interval: float, timeout: float) -> dict:
    deadline = time.time() + timeout
    last: dict = {}
    while time.time() < deadline:
        payload = c.admin("GET", c.ws(f"knowledge/{knowledge_id}/action/{action_id}"))
        last = c.data_of(payload) or {}
        state = str(last.get("state") or "")
        if state in TERMINAL or state.upper() in TERMINAL:
            return last
        time.sleep(interval)
    raise SystemExit(f"debug poll timeout after {timeout}s; last={last!r}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    p.add_argument("--knowledge-id", required=True)
    p.add_argument("--source-node-id", default=None, help="data-source node id (default: auto)")
    p.add_argument("--file", action="append", dest="files", help="Local file(s) for local data-source")
    p.add_argument("--source-url", default=None, help="URL for web data-source")
    p.add_argument("--selector", default="body", help="CSS selector for web (default body)")
    p.add_argument("--knowledge-base-json", default=None, help='JSON object for knowledge_base form')
    p.add_argument("--body-json", default=None, help="Full debug body (skips building data_source)")
    p.add_argument("--poll-interval", type=float, default=2.0)
    p.add_argument("--timeout", type=float, default=300.0)
    p.add_argument("--no-wait", action="store_true", help="Only start debug; do not poll")
    args = p.parse_args()
    require_yes(args.yes, f"debug knowledge workflow {args.knowledge_id}")

    c = client_from_args(args)
    try:
        if args.body_json:
            body = json.loads(Path(args.body_json).read_text(encoding="utf-8-sig"))
        else:
            wf_payload = c.data_of(c.admin("GET", c.ws(f"knowledge/{args.knowledge_id}/workflow")))
            work_flow = (wf_payload or {}).get("work_flow") or wf_payload or {}
            if isinstance(work_flow, dict) and "nodes" not in work_flow:
                # some responses nest again
                work_flow = work_flow.get("work_flow") or work_flow

            prefer = None
            if args.files:
                prefer = "data-source-local-node"
            elif args.source_url:
                prefer = "data-source-web-node"
            src = _pick_source_node(work_flow, prefer, args.source_node_id)
            node_id = src.get("id")
            data_source: dict = {"node_id": node_id}

            if args.files:
                file_list = []
                for f in args.files:
                    path = Path(f)
                    if not path.is_file():
                        print(f"file not found: {path}", file=sys.stderr)
                        return 1
                    file_list.append(_upload_file(c, args.knowledge_id, path))
                data_source["file_list"] = file_list
            elif args.source_url:
                data_source["source_url"] = args.source_url
                data_source["selector"] = args.selector or "body"
            else:
                p.error("provide --file, --source-url, or --body-json")

            knowledge_base = {}
            if args.knowledge_base_json:
                knowledge_base = json.loads(
                    Path(args.knowledge_base_json).read_text(encoding="utf-8-sig")
                )
            body = {"data_source": data_source, "knowledge_base": knowledge_base}

        started = c.admin("POST", c.ws(f"knowledge/{args.knowledge_id}/debug"), json_body=body)
        started_data = c.data_of(started) or {}
        action_id = started_data.get("id")
        if not action_id:
            print_json(started)
            print("no action id in debug response", file=sys.stderr)
            return 1

        if args.no_wait:
            print_json(started)
            return 0

        final = _poll(c, args.knowledge_id, str(action_id), args.poll_interval, args.timeout)
        print_json({"started": started_data, "result": final})
        state = str(final.get("state") or "")
        if state.upper() in ("SUCCESS",):
            return 0
        print(f"debug finished with state={state}", file=sys.stderr)
        return 1
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
