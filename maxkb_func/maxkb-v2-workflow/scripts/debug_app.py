#!/usr/bin/env python3
"""One-shot debug an application: open session → chat → evaluate reply.

Already have debug_open.py + debug_chat.py (两步). This script is the
save-then-smoke path: 开会话、提问、判断是否通、是否符合预期。

Examples:
  python debug_app.py --app-id APP --message "你好" --yes
  python debug_app.py --app-id APP --message "报销流程" --expect "依据" --min-chars 10 --yes
  python debug_app.py --name-prefix "[拓扑审核]" --message "请用一句话介绍你自己" --yes
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _lib.maxkb_client import (  # noqa: E402
    MaxKBError,
    add_common_args,
    client_from_args,
    print_json,
    require_yes,
)

ERROR_HINTS = (
    "Traceback",
    "NoneType",
    "异常",
    "报错",
    "Internal Server Error",
    "argument of type",
    "节点不能",
    "校验失败",
)


def _as_list(data: Any) -> list[dict]:
    if isinstance(data, dict):
        if isinstance(data.get("data"), list):
            return [x for x in data["data"] if isinstance(x, dict)]
        inner = data.get("data")
        if isinstance(inner, dict):
            for key in ("records", "list", "content"):
                if isinstance(inner.get(key), list):
                    return [x for x in inner[key] if isinstance(x, dict)]
        if isinstance(data.get("records"), list):
            return [x for x in data["records"] if isinstance(x, dict)]
        return [data] if data.get("id") else []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    return []


def resolve_targets(c, app_ids: list[str], name_prefix: str | None) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    seen: set[str] = set()
    for aid in app_ids:
        if aid in seen:
            continue
        seen.add(aid)
        name = aid
        try:
            d = c.data_of(c.admin("GET", c.ws(f"application/{aid}")))
            if isinstance(d, dict) and d.get("name"):
                name = str(d["name"])
        except MaxKBError:
            pass
        found.append((aid, name))

    if name_prefix:
        page, size = 1, 50
        while page <= 40:
            try:
                raw = c.admin("GET", c.ws(f"application/{page}/{size}"))
            except MaxKBError:
                for item in _as_list(c.admin("GET", c.ws("application"))):
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
    return found


def extract_chat_id(payload: Any) -> str:
    data = payload
    if isinstance(payload, dict) and "data" in payload:
        data = payload["data"]
    if isinstance(data, str) and data.strip():
        return data.strip()
    if isinstance(data, dict):
        for k in ("chat_id", "id", "chatId"):
            if data.get(k):
                return str(data[k])
    raise MaxKBError(f"cannot parse chat_id from open response: {payload!r}")


def extract_content(out: Any) -> str:
    if out is None:
        return ""
    if isinstance(out, str):
        return out
    if isinstance(out, dict):
        for k in ("content", "answer", "message", "text"):
            v = out.get(k)
            if isinstance(v, str) and v.strip():
                return v
        # nested data
        if isinstance(out.get("data"), dict):
            return extract_content(out["data"])
        if isinstance(out.get("data"), str):
            return out["data"]
    return json.dumps(out, ensure_ascii=False)[:2000]


def evaluate(
    content: str,
    *,
    expects: list[str],
    min_chars: int,
    forbid_error_hints: bool,
) -> dict[str, Any]:
    reasons: list[str] = []
    ok = True
    text = (content or "").strip()
    if not text:
        ok = False
        reasons.append("empty_content")
    if len(text) < min_chars:
        ok = False
        reasons.append(f"too_short<{min_chars}")
    for exp in expects:
        if exp and exp not in text:
            ok = False
            reasons.append(f"missing_expect:{exp}")
    if forbid_error_hints:
        for hint in ERROR_HINTS:
            if hint and hint in text:
                ok = False
                reasons.append(f"error_hint:{hint}")
                break
    return {
        "ok": ok,
        "chars": len(text),
        "reasons": reasons,
        "preview": text[:400],
    }


def debug_one(
    c,
    app_id: str,
    name: str,
    message: str,
    *,
    expects: list[str],
    min_chars: int,
    form_data: dict,
    timeout: float,
) -> dict[str, Any]:
    t0 = time.time()
    row: dict[str, Any] = {
        "id": app_id,
        "name": name,
        "message": message,
        "status": "FAIL",
        "通": False,
        "符合预期": False,
    }
    try:
        chat_id = extract_chat_id(c.admin("GET", c.ws(f"application/{app_id}/open")))
        row["chat_id"] = chat_id
        out = c.data_of(
            c.admin(
                "POST",
                f"/chat_message/{chat_id}",
                json_body={
                    "message": message,
                    "stream": False,
                    "re_chat": False,
                    "form_data": form_data,
                    "image_list": [],
                    "document_list": [],
                    "audio_list": [],
                    "other_list": [],
                },
                timeout=timeout,
            )
        )
        content = extract_content(out)
        row["content"] = content
        ev = evaluate(
            content,
            expects=expects,
            min_chars=min_chars,
            forbid_error_hints=True,
        )
        row["eval"] = ev
        row["elapsed_sec"] = round(time.time() - t0, 2)
        # 通 = pipeline ran and returned non-empty without hard error hints
        row["通"] = bool(content) and not any(
            r.startswith("error_hint:") or r == "empty_content" for r in ev["reasons"]
        )
        row["符合预期"] = ev["ok"]
        row["status"] = "OK" if ev["ok"] else ("PARTIAL" if row["通"] else "FAIL")
        return row
    except MaxKBError as e:
        row["elapsed_sec"] = round(time.time() - t0, 2)
        row["error"] = str(e)
        row["body"] = e.body
        row["status"] = "FAIL"
        row["通"] = False
        row["符合预期"] = False
        return row
    except Exception as e:
        row["elapsed_sec"] = round(time.time() - t0, 2)
        row["error"] = str(e)
        row["status"] = "FAIL"
        row["通"] = False
        row["符合预期"] = False
        return row


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    p.add_argument("--app-id", action="append", default=[], dest="app_ids")
    p.add_argument("--name-prefix", default=None, help='e.g. "[拓扑审核]"')
    p.add_argument("--message", default="你好，请用一句话说明你的能力。")
    p.add_argument(
        "--expect",
        action="append",
        default=[],
        dest="expects",
        help="Reply must contain this substring (repeatable)",
    )
    p.add_argument("--min-chars", type=int, default=5, help="Minimum reply length")
    p.add_argument("--form-data-json", default="{}")
    p.add_argument("--timeout", type=float, default=180.0, help="Per-request timeout seconds")
    p.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Only debug first N matched apps (0=all)",
    )
    p.add_argument("--out", default=None, help="Write full JSON report to this path")
    args = p.parse_args()
    if not args.app_ids and not args.name_prefix:
        p.error("provide --app-id and/or --name-prefix")

    require_yes(
        args.yes,
        f"debug chat app(s) message={args.message!r} "
        f"ids={args.app_ids or '-'} prefix={args.name_prefix or '-'}",
    )

    c = client_from_args(args)
    # allow longer LLM runs
    c.timeout = max(float(args.timeout), float(c.timeout or 120))

    targets = resolve_targets(c, args.app_ids, args.name_prefix)
    if args.limit and args.limit > 0:
        targets = targets[: args.limit]
    if not targets:
        print("No applications matched.", file=sys.stderr)
        return 1

    form_data = json.loads(args.form_data_json)
    results = []
    for app_id, name in targets:
        print(f"… debug {name} ({app_id})")
        row = debug_one(
            c,
            app_id,
            name,
            args.message,
            expects=args.expects,
            min_chars=args.min_chars,
            form_data=form_data,
            timeout=float(args.timeout),
        )
        mark = row["status"]
        preview = (row.get("content") or row.get("error") or "")[:120].replace("\n", " ")
        print(f"  {mark} 通={row['通']} 符合预期={row['符合预期']} {preview}")
        results.append(row)

    summary = {
        "total": len(results),
        "通": sum(1 for r in results if r.get("通")),
        "符合预期": sum(1 for r in results if r.get("符合预期")),
        "FAIL": sum(1 for r in results if r.get("status") == "FAIL"),
        "PARTIAL": sum(1 for r in results if r.get("status") == "PARTIAL"),
        "OK": sum(1 for r in results if r.get("status") == "OK"),
        "message": args.message,
        "expects": args.expects,
        "results": results,
    }
    print_json(summary)
    if args.out:
        Path(args.out).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"report written: {args.out}", file=sys.stderr)
    # exit 0 if all 通 (even PARTIAL); 1 if any hard FAIL
    return 0 if summary["FAIL"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
