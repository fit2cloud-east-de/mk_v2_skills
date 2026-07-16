#!/usr/bin/env python3
"""Create knowledge base: base | web | workflow."""
from __future__ import annotations

import argparse
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
    p.add_argument("--kind", choices=["base", "web", "workflow"], default="base")
    p.add_argument("--name", required=True)
    p.add_argument("--embedding-model-id", required=True)
    p.add_argument("--desc", default="")
    p.add_argument("--folder-id", default=None)
    p.add_argument("--source-url", help="Required for --kind web")
    p.add_argument("--selector", default="body")
    args = p.parse_args()
    require_yes(args.yes, f"create knowledge ({args.kind}) {args.name}")

    c = client_from_args(args)
    folder = args.folder_id or c.folder_id()
    body = {
        "name": args.name,
        "folder_id": folder,
        "desc": args.desc,
        "embedding_model_id": args.embedding_model_id,
    }
    if args.kind == "web":
        if not args.source_url:
            p.error("--source-url required for web")
        body["source_url"] = args.source_url
        body["selector"] = args.selector
        path = c.ws("knowledge/web")
    elif args.kind == "workflow":
        path = c.ws("knowledge/workflow")
    else:
        path = c.ws("knowledge/base")

    try:
        print_json(c.admin("POST", path, json_body=body))
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
