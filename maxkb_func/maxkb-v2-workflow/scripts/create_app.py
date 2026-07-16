#!/usr/bin/env python3
"""Create a WORK_FLOW application.

Either pass --from-json <file>, or --name with optional minimal skeleton.
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _lib.maxkb_client import (
    MaxKBError,
    add_common_args,
    client_from_args,
    print_json,
    require_yes,
)


def minimal_workflow(name: str, prologue: str) -> dict:
    return {
        "nodes": [
            {
                "id": "base-node",
                "type": "base-node",
                "x": 360,
                "y": 2760,
                "properties": {
                    "stepName": "基本信息",
                    "node_data": {
                        "name": name,
                        "desc": "",
                        "prologue": prologue,
                        "tts_type": "BROWSER",
                        "file_upload_enable": False,
                    },
                    "user_input_field_list": [],
                    "api_input_field_list": [],
                    "user_input_config": {"title": "用户输入"},
                },
            },
            {
                "id": "start-node",
                "type": "start-node",
                "x": 480,
                "y": 3340,
                "properties": {
                    "stepName": "开始",
                    "config": {
                        "fields": [{"label": "用户问题", "value": "question"}],
                        "globalFields": [
                            {"label": "当前时间", "value": "time"},
                            {"label": "历史聊天记录", "value": "history_context"},
                            {"label": "对话 ID", "value": "chat_id"},
                        ],
                    },
                },
            },
        ],
        "edges": [],
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    p.add_argument("--from-json", help="Full create body JSON file")
    p.add_argument("--name", help="App name when not using --from-json")
    p.add_argument("--desc", default="")
    p.add_argument("--prologue", default="你好，请问有什么可以帮您？")
    p.add_argument("--folder-id", default=None, help="Default: workspace id")
    args = p.parse_args()
    require_yes(args.yes, "create application")

    c = client_from_args(args)
    if args.from_json:
        body = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
    else:
        if not args.name:
            p.error("--name or --from-json required")
        folder = args.folder_id or c.folder_id()
        body = {
            "name": args.name,
            "desc": args.desc,
            "type": "WORK_FLOW",
            "folder_id": folder,
            "prologue": args.prologue,
            "work_flow": minimal_workflow(args.name, args.prologue),
        }
    # ensure unique edge/node ids not colliding if caller adds later
    _ = uuid.uuid4()
    try:
        print_json(c.admin("POST", c.ws("application"), json_body=body))
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
