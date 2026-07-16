"""MaxKB v2 HTTP client — used by all skill scripts (Python 3.11+).

Credentials: pass --host / --api-key / --workspace on every run.
Optional process env (MAXKB_*) is a fallback only — never load project .env files.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any
from urllib.parse import urljoin

import requests

if sys.version_info < (3, 11):
    raise RuntimeError(f"mk_v2_skills/maxkb_func requires Python >= 3.11, got {sys.version}")


class MaxKBError(RuntimeError):
    def __init__(self, message: str, status: int | None = None, body: Any = None):
        super().__init__(message)
        self.status = status
        self.body = body


class MaxKBClient:
    """Thin wrapper over MaxKB admin/chat APIs with Bearer auth."""

    def __init__(
        self,
        host: str | None = None,
        api_key: str | None = None,
        workspace: str | None = None,
        admin_prefix: str | None = None,
        chat_prefix: str | None = None,
        timeout: float = 120.0,
        resolve_workspace: bool = True,
    ):
        self.host = (host or os.environ.get("MAXKB_HOST", "")).rstrip("/")
        self.api_key = api_key or os.environ.get("MAXKB_API_KEY", "")
        self.workspace = workspace or os.environ.get("MAXKB_WORKSPACE", "default")
        self.admin_prefix = (admin_prefix or os.environ.get("MAXKB_ADMIN_PREFIX", "/admin/api")).rstrip("/")
        self.chat_prefix = (chat_prefix or os.environ.get("MAXKB_CHAT_PREFIX", "/chat/api")).rstrip("/")
        self.timeout = timeout
        self._resolved = False

        if not self.host:
            raise MaxKBError(
                "Host is required. Pass --host (or MAXKB_HOST for this process). "
                "Ask the user for the MaxKB base URL. Do not use project .env files."
            )
        if not self.api_key:
            raise MaxKBError(
                "API key is required. Pass --api-key (or MAXKB_API_KEY for this process). "
                "Use a regular-user key, not an admin key. Never write secrets into skill files "
                "or check in .env."
            )

        if resolve_workspace:
            self.ensure_workspace_id()

    @property
    def admin_base(self) -> str:
        return f"{self.host}{self.admin_prefix}"

    @property
    def chat_base(self) -> str:
        return f"{self.host}{self.chat_prefix}"

    def _headers(self, json_body: bool = True) -> dict[str, str]:
        h = {"Authorization": f"Bearer {self.api_key}"}
        if json_body:
            h["Content-Type"] = "application/json"
        return h

    def _url(self, base: str, path: str) -> str:
        path = path if path.startswith("/") else f"/{path}"
        return urljoin(base + "/", path.lstrip("/"))

    def request(
        self,
        method: str,
        path: str,
        *,
        base: str | None = None,
        params: dict | None = None,
        json_body: Any = None,
        data: Any = None,
        files: Any = None,
        stream: bool = False,
        timeout: float | None = None,
        check_biz_code: bool = True,
    ) -> Any:
        use_base = base or self.admin_base
        url = self._url(use_base, path)
        is_multipart = files is not None
        headers = self._headers(json_body=not is_multipart and data is None)
        if is_multipart:
            headers.pop("Content-Type", None)

        resp = requests.request(
            method.upper(),
            url,
            headers=headers,
            params=params,
            json=json_body,
            data=data,
            files=files,
            stream=stream,
            timeout=timeout or self.timeout,
        )
        if stream:
            if resp.status_code >= 400:
                raise MaxKBError(f"{method} {url} -> {resp.status_code}", resp.status_code, resp.text)
            return resp

        try:
            payload = resp.json() if resp.content else None
        except Exception:
            payload = resp.text

        if resp.status_code >= 400:
            raise MaxKBError(
                f"{method} {url} -> HTTP {resp.status_code}: {payload}",
                resp.status_code,
                payload,
            )

        # MaxKB often returns HTTP 200 with {"code": 500, "message": "..."}
        if check_biz_code and isinstance(payload, dict) and "code" in payload:
            code = payload.get("code")
            if code not in (200, 0, "200", "0", None):
                raise MaxKBError(
                    f"{method} {url} -> biz code={code}: {payload.get('message')}",
                    code if isinstance(code, int) else resp.status_code,
                    payload,
                )
        return payload

    def admin(self, method: str, path: str, **kwargs: Any) -> Any:
        return self.request(method, path, base=self.admin_base, **kwargs)

    def chat(self, method: str, path: str, **kwargs: Any) -> Any:
        return self.request(method, path, base=self.chat_base, **kwargs)

    def data_of(self, payload: Any) -> Any:
        """Unwrap Result envelope → data."""
        if isinstance(payload, dict) and "data" in payload:
            return payload["data"]
        return payload

    def ensure_workspace_id(self) -> str:
        """Resolve workspace display name (e.g. MyWorkspace) to UUID id."""
        if self._resolved:
            return self.workspace
        ws = self.workspace
        # already looks like uuid7 / uuid
        if len(ws) >= 32 and "-" in ws and ws.replace("-", "").isalnum():
            # still verify via by_user when possible
            try:
                lst = self.data_of(self.admin("GET", "/workspace/by_user", check_biz_code=True))
                ids = {item.get("id") for item in (lst or [])}
                if ws in ids or not lst:
                    self._resolved = True
                    return self.workspace
            except MaxKBError:
                self._resolved = True
                return self.workspace

        lst = self.data_of(self.admin("GET", "/workspace/by_user"))
        if not lst:
            # fallback profile.workspace_list
            profile = self.data_of(self.admin("GET", "/user/profile"))
            lst = (profile or {}).get("workspace_list") or []

        match = None
        for item in lst or []:
            if item.get("name") == ws or item.get("id") == ws:
                match = item
                break
        if not match:
            names = [f"{i.get('name')}({i.get('id')})" for i in (lst or [])]
            raise MaxKBError(
                f"Workspace '{ws}' not found for this API key. Available: {names or '(none)'}"
            )
        self.workspace = match["id"]
        self._resolved = True
        return self.workspace

    def ws(self, suffix: str) -> str:
        self.ensure_workspace_id()
        suffix = suffix.lstrip("/")
        return f"/workspace/{self.workspace}/{suffix}"

    def folder_id(self) -> str:
        """Root folder id equals workspace id in MaxKB EE."""
        return self.ensure_workspace_id()


def print_json(data: Any) -> None:
    sys.stdout.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def require_yes(yes: bool, action: str) -> None:
    """Write ops must pass --yes after human confirmation in the chat.

    Delete actions: agent must only reach here after the user explicitly
    requested deletion and replied with confirmation (see AUTH_AND_SAFETY §4).
    """
    if yes:
        return
    is_delete = action.upper().startswith("DELETE") or "DELETE " in action.upper()
    if is_delete:
        sys.stderr.write(
            f"[blocked] DELETE requires explicit user request + confirmation + --yes: {action}\n"
            "Do not delete resources unless the user asked for it.\n"
        )
    else:
        sys.stderr.write(
            f"[blocked] Write action requires --yes after user confirmation: {action}\n"
            "Risk: skills are for reference; prefer test env then migrate to prod.\n"
        )
    raise SystemExit(2)


def add_common_args(parser) -> None:
    parser.add_argument(
        "--host",
        default=None,
        help="MaxKB base URL (preferred). Else MAXKB_HOST in process env. No .env files.",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        dest="api_key",
        help="Regular-user API key (preferred). Else MAXKB_API_KEY. Never commit secrets.",
    )
    parser.add_argument(
        "--workspace",
        default=None,
        help="Workspace UUID or display name. Else MAXKB_WORKSPACE. Resolved via /workspace/by_user",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Confirm write/publish (for DELETE: only after user explicitly requested delete)",
    )


def client_from_args(args) -> MaxKBClient:
    return MaxKBClient(host=args.host, api_key=args.api_key, workspace=args.workspace)
