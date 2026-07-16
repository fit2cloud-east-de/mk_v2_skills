#!/usr/bin/env python3
"""List LLM models for AI-chat nodes (from workspace model_list)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _lib.maxkb_client import MaxKBError, add_common_args, client_from_args, print_json


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    args = p.parse_args()
    c = client_from_args(args)
    try:
        ml = c.data_of(c.admin("GET", c.ws("model_list"))) or {}
        llms = []
        for bucket in ("model", "shared_model"):
            for m in ml.get(bucket) or []:
                if str(m.get("model_type", "")).upper() == "LLM":
                    llms.append(m)
        print_json({"code": 200, "message": "成功", "data": llms})
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
