#!/usr/bin/env python3
"""One-shot: split file(s) then batch_create into knowledge (with --yes)."""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--knowledge-id", required=True)
    p.add_argument("--file", action="append", required=True, dest="files")
    p.add_argument("--limit", type=int, default=4096)
    p.add_argument("--host", default=None)
    p.add_argument("--api-key", default=None, dest="api_key")
    p.add_argument("--workspace", default=None)
    p.add_argument("--yes", "-y", action="store_true")
    args = p.parse_args()

    if not args.yes:
        print("[blocked] ingest requires --yes after user confirmation", file=sys.stderr)
        return 2

    common = []
    if args.host:
        common += ["--host", args.host]
    if args.api_key:
        common += ["--api-key", args.api_key]
    if args.workspace:
        common += ["--workspace", args.workspace]

    with tempfile.TemporaryDirectory() as td:
        preview = Path(td) / "split.json"
        cmd_split = [
            sys.executable,
            str(HERE / "split_document.py"),
            "--knowledge-id",
            args.knowledge_id,
            "--limit",
            str(args.limit),
            "--out",
            str(preview),
            *common,
        ]
        for f in args.files:
            cmd_split += ["--file", f]
        r1 = subprocess.run(cmd_split)
        if r1.returncode != 0:
            return r1.returncode

        cmd_batch = [
            sys.executable,
            str(HERE / "batch_create.py"),
            "--knowledge-id",
            args.knowledge_id,
            "--from-json",
            str(preview),
            "--normalize-split",
            "--yes",
            *common,
        ]
        r2 = subprocess.run(cmd_batch)
        return r2.returncode


if __name__ == "__main__":
    raise SystemExit(main())
