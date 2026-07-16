#!/usr/bin/env python3
"""Download latest MaxKB knowledge-workflow template (.kbwf) from Fit2Cloud app store.

Resolves downloadUrl via https://apps.fit2cloud.com/app-store/v1/software
(same catalog as https://apps.fit2cloud.com/maxkb/<slug>).

Presets:
  mineru-pdf-rag      → kbwf-mineru-pdf-rag   (online MinerU API; non-sensitive PDF)
  mineru-local-md     → kbwf-mineru-local-markdown (local MinerU Gradio)

Usage:
  python download_kbwf_template.py --preset mineru-pdf-rag --out ./tpl.kbwf
  python download_kbwf_template.py --app-id kbwf-mineru-local-markdown --out ./tpl.kbwf
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests

CATALOG_URL = "https://apps.fit2cloud.com/app-store/v1/software"

PRESETS: dict[str, str] = {
    "mineru-pdf-rag": "kbwf-mineru-pdf-rag",
    "mineru-local-md": "kbwf-mineru-local-markdown",
    "mineru-local-markdown": "kbwf-mineru-local-markdown",
}


def _find_app(catalog: list, app_id: str) -> dict:
    for group in catalog:
        apps = group.get("apps") if isinstance(group, dict) else None
        if not isinstance(apps, list):
            # catalog may be a flat list of apps
            continue
        for app in apps:
            if isinstance(app, dict) and app.get("id") == app_id:
                return app
    # flat list fallback
    for item in catalog:
        if isinstance(item, dict) and item.get("id") == app_id:
            return item
        if isinstance(item, dict):
            for app in item.get("apps") or []:
                if isinstance(app, dict) and app.get("id") == app_id:
                    return app
    raise SystemExit(f"app id not found in catalog: {app_id}")


def _pick_download_url(app: dict, version: str | None) -> tuple[str, str]:
    """Return (download_url, version_name). Prefer explicit version, else app latest."""
    versions = app.get("versions") or []
    if version:
        for v in versions:
            if not isinstance(v, dict):
                continue
            if v.get("name") == version or v.get("id") == version:
                url = v.get("downloadUrl")
                if not url:
                    raise SystemExit(f"version {version} has no downloadUrl")
                return url, str(v.get("name") or version)
        raise SystemExit(f"version not found: {version}")
    url = app.get("downloadUrl")
    if not url and versions:
        # first entry is usually latest
        v0 = versions[0]
        url = v0.get("downloadUrl")
        return url, str(v0.get("name") or "latest")
    if not url:
        raise SystemExit("no downloadUrl on app")
    # infer version from path .../2.0.0/file.kbwf
    parts = [p for p in urlparse(url).path.split("/") if p]
    ver = parts[-2] if len(parts) >= 2 else "latest"
    return url, ver


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--preset", choices=sorted(PRESETS), help="Convenient alias")
    p.add_argument("--app-id", help="Store app id, e.g. kbwf-mineru-pdf-rag")
    p.add_argument("--version", default=None, help="Optional version name like 2.0.0")
    p.add_argument("--out", required=True, help="Output .kbwf path")
    p.add_argument("--catalog-url", default=CATALOG_URL)
    p.add_argument("--timeout", type=float, default=120.0)
    args = p.parse_args()

    app_id = args.app_id or (PRESETS.get(args.preset) if args.preset else None)
    if not app_id:
        p.error("provide --preset or --app-id")

    r = requests.get(args.catalog_url, timeout=args.timeout)
    r.raise_for_status()
    catalog = r.json()
    if not isinstance(catalog, list):
        raise SystemExit("unexpected catalog shape")

    app = _find_app(catalog, app_id)
    url, ver = _pick_download_url(app, args.version)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    dl = requests.get(url, timeout=args.timeout)
    dl.raise_for_status()
    out.write_bytes(dl.content)

    meta = {
        "app_id": app_id,
        "name": app.get("name"),
        "version": ver,
        "download_url": url,
        "bytes": len(dl.content),
        "out": str(out.resolve()),
        "filename": unquote(Path(urlparse(url).path).name),
        "store_page": f"https://apps.fit2cloud.com/maxkb/{app_id}",
    }
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
