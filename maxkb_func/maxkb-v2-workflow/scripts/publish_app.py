#!/usr/bin/env python3
"""Publish one or more MaxKB applications (一键发布).

Examples:
  python publish_app.py --app-id APP --yes
  python publish_app.py --app-id A1 --app-id A2 --yes
  python publish_app.py --name-prefix "[拓扑审核]" --yes
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _lib.maxkb_client import (
    MaxKBError,
    add_common_args,
    client_from_args,
    print_json,
    require_yes,
)


def _as_list(data: Any) -> list[dict]:
    if isinstance(data, dict):
        if isinstance(data.get("data"), list):
            return [x for x in data["data"] if isinstance(x, dict)]
        if isinstance(data.get("records"), list):
            return [x for x in data["records"] if isinstance(x, dict)]
        # unwrap {code,data:{records|list}}
        inner = data.get("data")
        if isinstance(inner, dict):
            for key in ("records", "list", "content"):
                if isinstance(inner.get(key), list):
                    return [x for x in inner[key] if isinstance(x, dict)]
        return [data] if data.get("id") else []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    return []


def resolve_app_ids(c, app_ids: list[str], name_prefix: str | None) -> list[tuple[str, str]]:
    """Return list of (id, name)."""
    found: list[tuple[str, str]] = []
    seen: set[str] = set()

    for aid in app_ids:
        if aid in seen:
            continue
        seen.add(aid)
        name = aid
        try:
            detail = c.admin("GET", c.ws(f"application/{aid}"))
            d = detail.get("data") if isinstance(detail, dict) else detail
            if isinstance(d, dict) and d.get("name"):
                name = d["name"]
        except MaxKBError:
            pass
        found.append((aid, name))

    if name_prefix:
        # Prefer paginated scan to catch all matches
        page = 1
        size = 50
        while True:
            try:
                raw = c.admin("GET", c.ws(f"application/{page}/{size}"))
            except MaxKBError:
                raw = c.admin("GET", c.ws("application"))
                items = _as_list(raw)
                for item in items:
                    name = str(item.get("name") or "")
                    aid = str(item.get("id") or "")
                    if aid and name_prefix in name and aid not in seen:
                        seen.add(aid)
                        found.append((aid, name))
                break
            items = _as_list(raw)
            if not items:
                break
            for item in items:
                name = str(item.get("name") or "")
                aid = str(item.get("id") or "")
                if aid and name_prefix in name and aid not in seen:
                    seen.add(aid)
                    found.append((aid, name))
            if len(items) < size:
                break
            page += 1
            if page > 40:
                break

    return found


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    p.add_argument(
        "--app-id",
        action="append",
        default=[],
        dest="app_ids",
        help="Application id (repeatable)",
    )
    p.add_argument(
        "--name-prefix",
        default=None,
        help='Publish all apps whose name contains this string, e.g. "[拓扑审核]"',
    )
    args = p.parse_args()
    if not args.app_ids and not args.name_prefix:
        p.error("provide --app-id and/or --name-prefix")

    targets_hint = ", ".join(args.app_ids) if args.app_ids else ""
    if args.name_prefix:
        targets_hint = (targets_hint + f" name~={args.name_prefix}").strip()
    require_yes(args.yes, f"publish application(s): {targets_hint}")

    c = client_from_args(args)
    try:
        targets = resolve_app_ids(c, args.app_ids, args.name_prefix)
        if not targets:
            print("No applications matched.", file=sys.stderr)
            return 1

        results = []
        ok = 0
        fail = 0
        for app_id, name in targets:
            try:
                resp = c.admin("PUT", c.ws(f"application/{app_id}/publish"), json_body={})
                results.append({"id": app_id, "name": name, "status": "OK", "response": resp})
                ok += 1
                print(f"OK  {name} ({app_id})")
            except MaxKBError as e:
                results.append(
                    {
                        "id": app_id,
                        "name": name,
                        "status": "FAIL",
                        "error": str(e),
                        "body": e.body,
                    }
                )
                fail += 1
                print(f"FAIL {name} ({app_id}): {e}", file=sys.stderr)

        print_json({"published_ok": ok, "published_fail": fail, "results": results})
        return 0 if fail == 0 else 1
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
