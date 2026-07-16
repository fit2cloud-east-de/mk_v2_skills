#!/usr/bin/env python3
"""Save / update application work_flow (or other editable fields).

Usage:
  python save_workflow.py --app-id ID --workflow-json path.json --yes
  python save_workflow.py --app-id ID --body-json path.json --yes
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
    p.add_argument("--app-id", required=True)
    p.add_argument("--workflow-json", help="File with {nodes, edges}")
    p.add_argument("--body-json", help="Full PUT body JSON")
    args = p.parse_args()
    require_yes(args.yes, f"update application {args.app_id}")

    if args.body_json:
        body = json.loads(Path(args.body_json).read_text(encoding="utf-8"))
    elif args.workflow_json:
        wf = json.loads(Path(args.workflow_json).read_text(encoding="utf-8"))
        body = {"work_flow": wf}
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
