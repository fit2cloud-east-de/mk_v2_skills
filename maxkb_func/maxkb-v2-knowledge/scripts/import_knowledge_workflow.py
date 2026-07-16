#!/usr/bin/env python3
"""Import a .kbwf file into an existing workflow knowledge base.

API: POST {ADMIN_API}/workspace/{WS}/knowledge/{id}/workflow/import
multipart field: file

WARNING: This **overwrites** the knowledge base's current workflow definition
(same as UI confirm). Never point --knowledge-id at a user's existing library
unless they explicitly confirmed overwrite. Prefer: create a NEW workflow KB,
then import into that new id.

Usage:
  python import_knowledge_workflow.py --knowledge-id KID --file ./tpl.kbwf --yes \\
    --host HOST --workspace WS --api-key KEY
"""
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
    p.add_argument("--knowledge-id", required=True, help="Target workflow knowledge id")
    p.add_argument("--file", required=True, help="Path to .kbwf template")
    p.add_argument(
        "--allow-overwrite",
        action="store_true",
        help="Acknowledge that import overwrites the KB's current workflow",
    )
    args = p.parse_args()

    path = Path(args.file)
    if not path.is_file():
        print(f"file not found: {path}", file=sys.stderr)
        return 1
    if path.suffix.lower() != ".kbwf":
        print(f"warning: expected .kbwf, got {path.suffix}", file=sys.stderr)

    require_yes(
        args.yes,
        f"IMPORT workflow into knowledge {args.knowledge_id} (overwrites work_flow)",
    )
    if not args.allow_overwrite:
        print(
            "[blocked] Import overwrites the knowledge workflow. "
            "Pass --allow-overwrite only after the user confirmed "
            "(prefer a newly created empty workflow KB).",
            file=sys.stderr,
        )
        return 2

    c = client_from_args(args)
    try:
        with path.open("rb") as f:
            files = {"file": (path.name, f, "application/octet-stream")}
            print_json(
                c.admin(
                    "POST",
                    c.ws(f"knowledge/{args.knowledge_id}/workflow/import"),
                    files=files,
                )
            )
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
