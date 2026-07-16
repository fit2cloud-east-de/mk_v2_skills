#!/usr/bin/env python3
"""Debug tool code without saving (POST /tool/debug)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _lib.maxkb_client import MaxKBError, add_common_args, client_from_args, print_json


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    p.add_argument("--code", default=None)
    p.add_argument("--code-file", default=None)
    p.add_argument("--input-fields-json", default="[]")
    p.add_argument("--input-fields-file")
    p.add_argument("--debug-fields-json", default="[]", help='[{"name":"x","value":"1"}]')
    p.add_argument("--debug-fields-file")
    p.add_argument("--init-fields-json", default="[]")
    p.add_argument("--init-params-json", default="{}")
    args = p.parse_args()

    def load_json_arg(raw: str, file_path: str | None):
        if file_path:
            return json.loads(Path(file_path).read_text(encoding="utf-8"))
        return json.loads(raw)

    if args.code_file:
        code = Path(args.code_file).read_text(encoding="utf-8")
    elif args.code is not None:
        code = args.code
    else:
        p.error("--code or --code-file required")

    body = {
        "code": code,
        "input_field_list": load_json_arg(args.input_fields_json, args.input_fields_file),
        "init_field_list": json.loads(args.init_fields_json),
        "init_params": json.loads(args.init_params_json),
        "debug_field_list": load_json_arg(args.debug_fields_json, args.debug_fields_file),
    }
    c = client_from_args(args)
    try:
        print_json(c.admin("POST", c.ws("tool/debug"), json_body=body))
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
