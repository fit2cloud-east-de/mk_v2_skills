#!/usr/bin/env python3
"""Send debug chat message (admin /chat_message/{chat_id})."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _lib.maxkb_client import MaxKBError, add_common_args, client_from_args


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    p.add_argument("--chat-id", required=True)
    p.add_argument("--message", required=True)
    p.add_argument("--stream", action="store_true", default=True)
    p.add_argument("--no-stream", action="store_true")
    p.add_argument("--re-chat", action="store_true")
    p.add_argument("--form-data-json", default="{}", help='e.g. \'{"role":"工程师"}\'')
    p.add_argument("--body-json", help="Override full body JSON file")
    args = p.parse_args()
    stream = False if args.no_stream else True

    if args.body_json:
        body = json.loads(Path(args.body_json).read_text(encoding="utf-8"))
    else:
        body = {
            "message": args.message,
            "stream": stream,
            "re_chat": args.re_chat,
            "form_data": json.loads(args.form_data_json),
            "image_list": [],
            "document_list": [],
            "audio_list": [],
            "other_list": [],
        }

    c = client_from_args(args)
    try:
        if stream:
            resp = c.admin("POST", f"/chat_message/{args.chat_id}", json_body=body, stream=True)
            for chunk in resp.iter_content(chunk_size=None):
                if chunk:
                    sys.stdout.buffer.write(chunk)
                    sys.stdout.buffer.flush()
            sys.stdout.write("\n")
        else:
            from _lib.maxkb_client import print_json

            print_json(c.admin("POST", f"/chat_message/{args.chat_id}", json_body=body))
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
