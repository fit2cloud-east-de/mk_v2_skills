#!/usr/bin/env python3
"""OpenAI-compatible chat completions (use APPLICATION agent- key via --api-key)."""
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
    p.add_argument("--app-id", required=True)
    p.add_argument("--message", required=True)
    p.add_argument("--stream", action="store_true")
    p.add_argument("--form-data-json", default="{}")
    args = p.parse_args()
    body = {
        "messages": [{"role": "user", "content": args.message}],
        "stream": args.stream,
        "re_chat": False,
        "form_data": json.loads(args.form_data_json),
    }
    c = client_from_args(args)
    try:
        if args.stream:
            resp = c.chat(
                "POST",
                f"/{args.app_id}/chat/completions",
                json_body=body,
                stream=True,
            )
            for chunk in resp.iter_content(chunk_size=None):
                if chunk:
                    sys.stdout.buffer.write(chunk)
                    sys.stdout.buffer.flush()
            sys.stdout.write("\n")
        else:
            print_json(c.chat("POST", f"/{args.app_id}/chat/completions", json_body=body))
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
