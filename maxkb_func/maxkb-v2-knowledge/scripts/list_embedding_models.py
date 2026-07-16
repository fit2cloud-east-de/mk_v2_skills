#!/usr/bin/env python3
"""List embedding models. Prefer workspace model_list (API-key friendly)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _lib.maxkb_client import MaxKBError, add_common_args, client_from_args, print_json


def _pick_embedding(payload) -> list:
    data = payload
    if isinstance(payload, dict) and "data" in payload:
        data = payload["data"]
    out = []
    if isinstance(data, dict):
        for bucket in ("model", "shared_model"):
            for m in data.get(bucket) or []:
                if str(m.get("model_type", "")).upper() == "EMBEDDING":
                    out.append(m)
    elif isinstance(data, list):
        for m in data:
            if str((m or {}).get("model_type", "")).upper() == "EMBEDDING":
                out.append(m)
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    args = p.parse_args()
    c = client_from_args(args)
    try:
        # Prefer model_list / model — knowledge/embedding_model often fails under user- API key
        ml = c.admin("GET", c.ws("model_list"))
        emb = _pick_embedding(ml)
        if not emb:
            raw = c.admin("GET", c.ws("model"))
            emb = _pick_embedding(raw) or [
                m
                for m in (c.data_of(raw) or [])
                if str((m or {}).get("model_type", "")).upper() == "EMBEDDING"
            ]
        print_json({"code": 200, "message": "成功", "data": emb})
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
