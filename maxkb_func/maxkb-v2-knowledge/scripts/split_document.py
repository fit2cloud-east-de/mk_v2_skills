#!/usr/bin/env python3
"""Preview document split (multipart). Prints split preview JSON."""
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
    p.add_argument("--knowledge-id", required=True)
    p.add_argument("--file", action="append", required=True, dest="files", help="Can repeat")
    p.add_argument("--limit", type=int, default=4096)
    p.add_argument("--no-filter", action="store_true", help="Disable auto clean (default: filter on)")
    p.add_argument("--pattern", action="append", dest="patterns", default=[])
    p.add_argument("--out", help="Save response JSON")
    args = p.parse_args()

    opened = []
    try:
        files = []
        for f in args.files:
            path = Path(f)
            fh = path.open("rb")
            opened.append(fh)
            files.append(("file", (path.name, fh)))

        data = [("limit", str(args.limit)), ("with_filter", "false" if args.no_filter else "true")]
        for pat in args.patterns:
            data.append(("patterns", pat))

        c = client_from_args(args)
        resp = c.admin(
            "POST",
            c.ws(f"knowledge/{args.knowledge_id}/document/split"),
            data=data,
            files=files,
            timeout=3600,
        )
        print_json(resp)
        if args.out:
            Path(args.out).write_text(json.dumps(resp, ensure_ascii=False, indent=2), encoding="utf-8")
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1
    finally:
        for fh in opened:
            fh.close()


if __name__ == "__main__":
    raise SystemExit(main())
