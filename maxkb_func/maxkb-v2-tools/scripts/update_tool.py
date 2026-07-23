#!/usr/bin/env python3
"""Update tool by id.

Usage:
  python update_tool.py --tool-id ID --body-json patch.json --yes
  python update_tool.py --tool-id ID --code-file ./a.py --yes
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
    p.add_argument("--tool-id", required=True)
    p.add_argument("--body-json", help="Partial or full PUT body JSON file")
    p.add_argument("--name", default=None)
    p.add_argument("--desc", default=None)
    p.add_argument("--code-file", default=None)
    p.add_argument("--input-fields-file", default=None)
    p.add_argument("--init-fields-file", default=None)
    p.add_argument("--init-params-file", help="JSON object → init_params (encrypted server-side)")
    p.add_argument("--active", action="store_true")
    p.add_argument("--inactive", action="store_true")
    args = p.parse_args()
    require_yes(args.yes, f"update tool {args.tool_id}")

    body: dict = {}
    if args.body_json:
        body = json.loads(Path(args.body_json).read_text(encoding="utf-8-sig"))
    if args.name is not None:
        body["name"] = args.name
    if args.desc is not None:
        body["desc"] = args.desc
    if args.code_file:
        body["code"] = Path(args.code_file).read_text(encoding="utf-8-sig")
    if args.input_fields_file:
        body["input_field_list"] = json.loads(
            Path(args.input_fields_file).read_text(encoding="utf-8-sig")
        )
    if args.init_fields_file:
        body["init_field_list"] = json.loads(
            Path(args.init_fields_file).read_text(encoding="utf-8-sig")
        )
    if args.init_params_file:
        body["init_params"] = json.loads(
            Path(args.init_params_file).read_text(encoding="utf-8-sig")
        )
    if args.active:
        body["is_active"] = True
    if args.inactive:
        body["is_active"] = False
    if not body:
        p.error("provide --body-json and/or field flags")

    c = client_from_args(args)
    try:
        print_json(c.admin("PUT", c.ws(f"tool/{args.tool_id}"), json_body=body))
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
