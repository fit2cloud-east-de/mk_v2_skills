#!/usr/bin/env python3
"""Create a custom / DATA_SOURCE / other tool.

Provide --code-file or --code. Optional input/init field JSON files.
For DATA_SOURCE rules see ../data-source-tools.md
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


def _load_json(raw: str, file_path: str | None):
    if file_path:
        return json.loads(Path(file_path).read_text(encoding="utf-8-sig"))
    return json.loads(raw)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    p.add_argument("--name", required=True)
    p.add_argument("--desc", default="")
    p.add_argument("--code", default=None)
    p.add_argument("--code-file", default=None)
    p.add_argument("--folder-id", default=None)
    p.add_argument(
        "--tool-type",
        default="CUSTOM",
        help="CUSTOM | DATA_SOURCE | MCP | WORKFLOW | SKILL | …",
    )
    p.add_argument("--input-fields-json", default="[]")
    p.add_argument("--input-fields-file", help="JSON file for input_field_list (preferred on Windows)")
    p.add_argument("--init-fields-json", default="[]")
    p.add_argument("--init-fields-file", help="JSON file for init_field_list")
    p.add_argument("--active", action="store_true", default=True)
    p.add_argument("--inactive", action="store_true")
    p.add_argument("--from-json", help="Full create body")
    args = p.parse_args()
    require_yes(args.yes, f"create tool ({args.tool_type}) {args.name}")

    if args.from_json:
        body = json.loads(Path(args.from_json).read_text(encoding="utf-8-sig"))
    else:
        if args.code_file:
            code = Path(args.code_file).read_text(encoding="utf-8-sig")
        elif args.code is not None:
            code = args.code
        else:
            p.error("provide --code, --code-file, or --from-json")
        body = {
            "name": args.name,
            "desc": args.desc,
            "code": code,
            "folder_id": args.folder_id,
            "tool_type": args.tool_type,
            "input_field_list": _load_json(args.input_fields_json, args.input_fields_file),
            "init_field_list": _load_json(args.init_fields_json, args.init_fields_file),
            "is_active": False if args.inactive else True,
        }

    if body.get("tool_type") == "DATA_SOURCE" and "get_down_file_list" in (body.get("code") or ""):
        if "get_download_file_list" not in body["code"]:
            print(
                "[warn] code defines get_down_file_list but runtime looks for "
                "get_download_file_list — download branch may never run; "
                "see data-source-tools.md",
                file=sys.stderr,
            )

    c = client_from_args(args)
    if body.get("folder_id") is None:
        body["folder_id"] = c.folder_id()
    want_active = bool(body.get("is_active", True))
    try:
        created = c.admin("POST", c.ws("tool"), json_body=body)
        data = c.data_of(created) or {}
        tool_id = data.get("id")
        if tool_id and want_active and not data.get("is_active"):
            created = c.admin("PUT", c.ws(f"tool/{tool_id}"), json_body={"is_active": True})
        print_json(created)
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
