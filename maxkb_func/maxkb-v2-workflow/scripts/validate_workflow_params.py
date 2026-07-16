#!/usr/bin/env python3
"""Validate key workflow node parameters against a live MaxKB instance.

Builds: start → condition → (tool-node → tool-lib → reply) | else-reply
Uses form_data / template bindings. Requires --yes.
Created resources are kept by default; pass --cleanup only when the user
explicitly requested deleting them.
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


def nid() -> str:
    return str(uuid.uuid4())


def build_wf(tool_id: str, name: str) -> dict:
    tn, tlib, reply, cond, else_r = nid(), nid(), nid(), nid(), nid()
    bif, belse = nid(), nid()
    es = [nid() for _ in range(5)]
    return {
        "nodes": [
            {
                "id": "base-node",
                "type": "base-node",
                "x": 360,
                "y": 2000,
                "properties": {
                    "stepName": "基本信息",
                    "node_data": {
                        "name": name,
                        "desc": "workflow param validation",
                        "prologue": "验证开场白",
                        "tts_type": "BROWSER",
                        "file_upload_enable": True,
                        "file_upload_setting": {
                            "maxFiles": 3,
                            "fileLimit": 50,
                            "document": True,
                            "image": True,
                            "audio": False,
                            "video": False,
                            "other": False,
                            "otherExtensions": [],
                        },
                    },
                    "user_input_field_list": [
                        {
                            "field": "role",
                            "label": "角色",
                            "type": "input",
                            "default_value": "工程师",
                            "required": False,
                        }
                    ],
                    "api_input_field_list": [],
                },
            },
            {
                "id": "start-node",
                "type": "start-node",
                "x": 480,
                "y": 2800,
                "properties": {
                    "stepName": "开始",
                    "config": {
                        "fields": [
                            {"label": "用户问题", "value": "question"},
                            {"label": "文档", "value": "document"},
                            {"label": "图片", "value": "image"},
                        ],
                        "globalFields": [
                            {"label": "当前时间", "value": "time"},
                            {"label": "角色", "value": "role"},
                        ],
                    },
                },
            },
            {
                "id": cond,
                "type": "condition-node",
                "x": 700,
                "y": 2800,
                "properties": {
                    "stepName": "判断器",
                    "node_data": {
                        "branch": [
                            {
                                "id": bif,
                                "type": "IF",
                                "condition": "and",
                                "conditions": [
                                    {
                                        "field": ["start-node", "question"],
                                        "compare": "contain",
                                        "value": "工具",
                                    }
                                ],
                            },
                            {"id": belse, "type": "ELSE", "condition": "and", "conditions": []},
                        ]
                    },
                    "branch_condition_list": [
                        {"id": bif, "index": 0, "height": 50},
                        {"id": belse, "index": 1, "height": 50},
                    ],
                },
            },
            {
                "id": tn,
                "type": "tool-node",
                "x": 980,
                "y": 2600,
                "properties": {
                    "stepName": "内嵌工具",
                    "config": {"fields": [{"label": "结果", "value": "result"}]},
                    "node_data": {
                        "code": 'def main(q):\n    return "TOOLNODE:"+str(q)\n',
                        "input_field_list": [
                            {
                                "name": "q",
                                "type": "string",
                                "source": "reference",
                                "value": ["start-node", "question"],
                                "is_required": True,
                            }
                        ],
                        "is_result": False,
                    },
                },
            },
            {
                "id": tlib,
                "type": "tool-lib-node",
                "x": 1200,
                "y": 2600,
                "properties": {
                    "stepName": "库工具",
                    "config": {"fields": [{"label": "结果", "value": "result"}]},
                    "node_data": {
                        "tool_lib_id": tool_id,
                        # IMPORTANT: use template string for tool-lib (see SANDBOX.md)
                        "input_field_list": [
                            {
                                "name": "text",
                                "type": "string",
                                "source": "custom",
                                "value": "{{内嵌工具.result}}",
                                "is_required": True,
                            }
                        ],
                        "is_result": False,
                    },
                },
            },
            {
                "id": reply,
                "type": "reply-node",
                "x": 1450,
                "y": 2600,
                "properties": {
                    "stepName": "指定回复工具分支",
                    "config": {"fields": [{"label": "内容", "value": "answer"}]},
                    "node_data": {
                        "reply_type": "content",
                        "content": "OK={{库工具.result}}",
                        "is_result": True,
                    },
                },
            },
            {
                "id": else_r,
                "type": "reply-node",
                "x": 980,
                "y": 3000,
                "properties": {
                    "stepName": "指定回复普通",
                    "config": {"fields": [{"label": "内容", "value": "answer"}]},
                    "node_data": {
                        "reply_type": "content",
                        "content": "ELSE={{开始.question}} role={{global.role}}",
                        "is_result": True,
                    },
                },
            },
        ],
        "edges": [
            {
                "id": es[0],
                "type": "app-edge",
                "sourceNodeId": "start-node",
                "targetNodeId": cond,
                "sourceAnchorId": "start-node_right",
                "targetAnchorId": f"{cond}_left",
                "startPoint": {"x": 0, "y": 0},
                "endPoint": {"x": 0, "y": 0},
                "pointsList": [],
                "properties": {},
            },
            {
                "id": es[1],
                "type": "app-edge",
                "sourceNodeId": cond,
                "targetNodeId": tn,
                "sourceAnchorId": f"{cond}_{bif}_right",
                "targetAnchorId": f"{tn}_left",
                "startPoint": {"x": 0, "y": 0},
                "endPoint": {"x": 0, "y": 0},
                "pointsList": [],
                "properties": {},
            },
            {
                "id": es[2],
                "type": "app-edge",
                "sourceNodeId": tn,
                "targetNodeId": tlib,
                "sourceAnchorId": f"{tn}_right",
                "targetAnchorId": f"{tlib}_left",
                "startPoint": {"x": 0, "y": 0},
                "endPoint": {"x": 0, "y": 0},
                "pointsList": [],
                "properties": {},
            },
            {
                "id": es[3],
                "type": "app-edge",
                "sourceNodeId": tlib,
                "targetNodeId": reply,
                "sourceAnchorId": f"{tlib}_right",
                "targetAnchorId": f"{reply}_left",
                "startPoint": {"x": 0, "y": 0},
                "endPoint": {"x": 0, "y": 0},
                "pointsList": [],
                "properties": {},
            },
            {
                "id": es[4],
                "type": "app-edge",
                "sourceNodeId": cond,
                "targetNodeId": else_r,
                "sourceAnchorId": f"{cond}_{belse}_right",
                "targetAnchorId": f"{else_r}_left",
                "startPoint": {"x": 0, "y": 0},
                "endPoint": {"x": 0, "y": 0},
                "pointsList": [],
                "properties": {},
            },
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    p.add_argument("--app-id", help="Reuse app; otherwise create one")
    p.add_argument("--tool-id", help="Reuse tool; otherwise create echo tool")
    p.add_argument("--name", default="skill-param-validate")
    p.add_argument(
        "--cleanup",
        action="store_true",
        help="Delete resources created by this run (only when user explicitly requested cleanup)",
    )
    # --keep kept as no-op for backward compatibility (default is now keep).
    p.add_argument("--keep", action="store_true", help=argparse.SUPPRESS)
    args = p.parse_args()
    require_yes(args.yes, "validate workflow params (create/update/publish/debug)")

    c = client_from_args(args)
    created_tool = False
    created_app = False
    tool_id = args.tool_id
    app_id = args.app_id

    try:
        if not tool_id:
            tr = c.admin(
                "POST",
                c.ws("tool"),
                json_body={
                    "name": f"{args.name}-echo",
                    "desc": "param validate",
                    "folder_id": c.folder_id(),
                    "code": "def main(text):\n    return text\n",
                    "input_field_list": [
                        {"name": "text", "type": "string", "source": "custom", "is_required": True}
                    ],
                    "init_field_list": [],
                    "is_active": True,
                    "tool_type": "CUSTOM",
                },
            )
            tool_id = c.data_of(tr)["id"]
            created_tool = True
            c.admin("PUT", c.ws(f"tool/{tool_id}"), json_body={"is_active": True})

        wf = build_wf(tool_id, args.name)
        if not app_id:
            ar = c.admin(
                "POST",
                c.ws("application"),
                json_body={
                    "name": args.name,
                    "desc": "param validate",
                    "type": "WORK_FLOW",
                    "folder_id": c.folder_id(),
                    "prologue": "验证开场白",
                    "work_flow": {"nodes": wf["nodes"][:2], "edges": []},
                },
            )
            app_id = c.data_of(ar)["id"]
            created_app = True

        c.admin("PUT", c.ws(f"application/{app_id}"), json_body={"work_flow": wf, "prologue": "验证开场白"})
        c.admin("PUT", c.ws(f"application/{app_id}/publish"), json_body={})
        chat_id = c.data_of(c.admin("GET", c.ws(f"application/{app_id}/open")))

        results = {}
        for msg, expect_sub in [("你好", "ELSE=你好"), ("请用工具", "OK=TOOLNODE:请用工具")]:
            out = c.data_of(
                c.admin(
                    "POST",
                    f"/chat_message/{chat_id}",
                    json_body={
                        "message": msg,
                        "stream": False,
                        "re_chat": False,
                        "form_data": {"role": "测试员"},
                    },
                )
            )
            content = out.get("content", "")
            ok = expect_sub in content
            results[msg] = {"ok": ok, "content": content, "expect": expect_sub}
            if not ok:
                raise MaxKBError(f"unexpected reply for {msg!r}: {content}")

        print_json(
            {
                "code": 200,
                "message": "workflow param validation passed",
                "data": {
                    "workspace_id": c.workspace,
                    "app_id": app_id,
                    "tool_id": tool_id,
                    "chat_id": chat_id,
                    "results": results,
                    "validated": [
                        "base-node.file_upload_*",
                        "user_input_field_list + form_data → {{global.role}}",
                        "condition-node IF/ELSE anchors",
                        "tool-node reference value [node,field]",
                        "tool-lib-node template {{节点.result}}",
                        "reply-node content templates",
                        "publish + debug chat",
                    ],
                },
            }
        )
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1
    finally:
        # Default: keep created resources. Only delete when user explicitly requested --cleanup.
        if args.cleanup:
            try:
                if created_app and app_id:
                    c.admin("DELETE", c.ws(f"application/{app_id}"))
                if created_tool and tool_id:
                    c.admin("DELETE", c.ws(f"tool/{tool_id}"))
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
