#!/usr/bin/env python3
"""PUT document/batch_create from a JSON file (array of docs with paragraphs)."""
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


def _normalize_split_to_batch(split_payload) -> list:
    """Best-effort: accept already-batch array or common split preview shapes."""
    if isinstance(split_payload, dict) and "data" in split_payload:
        split_payload = split_payload["data"]
    if isinstance(split_payload, list):
        if split_payload and isinstance(split_payload[0], dict) and "paragraphs" in split_payload[0]:
            return split_payload
        docs = []
        for item in split_payload:
            if not isinstance(item, dict):
                continue
            if "paragraphs" in item:
                docs.append(item)
                continue
            name = item.get("name") or item.get("file_name") or "document"
            paragraphs = item.get("paragraphs")
            if paragraphs is None and "content" in item:
                contents = item["content"]
                paragraphs = []
                if isinstance(contents, list):
                    for block in contents:
                        if isinstance(block, str):
                            paragraphs.append(
                                {"title": "", "content": block, "problem_list": [], "is_active": True}
                            )
                        elif isinstance(block, dict):
                            paragraphs.append(
                                {
                                    "title": block.get("title", ""),
                                    "content": block.get("content") or block.get("text") or "",
                                    "problem_list": block.get("problem_list", []),
                                    "is_active": block.get("is_active", True),
                                }
                            )
                elif isinstance(contents, str):
                    paragraphs = [
                        {"title": "", "content": contents, "problem_list": [], "is_active": True}
                    ]
            if paragraphs is not None:
                docs.append(
                    {
                        "name": name,
                        "paragraphs": paragraphs,
                        "source_file_id": item.get("source_file_id"),
                    }
                )
        if docs:
            return docs
    if isinstance(split_payload, dict):
        return _normalize_split_to_batch([split_payload])
    raise ValueError("Unrecognized split/batch JSON shape; pass a batch_create array")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    p.add_argument("--knowledge-id", required=True)
    p.add_argument("--from-json", required=True, help="batch_create array or split preview JSON")
    p.add_argument("--normalize-split", action="store_true", help="Try convert split preview → batch body")
    args = p.parse_args()
    require_yes(args.yes, f"batch_create documents into {args.knowledge_id}")

    raw = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
    body = _normalize_split_to_batch(raw) if args.normalize_split else raw
    if not isinstance(body, list):
        # unwrap Result
        if isinstance(body, dict) and isinstance(body.get("data"), list):
            body = body["data"]
        else:
            p.error("JSON must be an array of {name, paragraphs}")

    c = client_from_args(args)
    try:
        print_json(
            c.admin(
                "PUT",
                c.ws(f"knowledge/{args.knowledge_id}/document/batch_create"),
                json_body=body,
                timeout=600,
            )
        )
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
