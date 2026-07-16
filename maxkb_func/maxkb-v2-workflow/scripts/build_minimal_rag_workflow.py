#!/usr/bin/env python3
"""Build a minimal RAG work_flow JSON to stdout (for save_workflow.py).

Does not call the API — only generates graph JSON.
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path


def nid() -> str:
    return str(uuid.uuid4())


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--name", default="RAG-Demo")
    p.add_argument("--knowledge-id", required=True)
    p.add_argument("--model-id", required=True)
    p.add_argument("--prologue", default="你好")
    p.add_argument("--out", help="Write to file instead of stdout")
    args = p.parse_args()

    sk_id, ai_id = nid(), nid()
    e1, e2 = nid(), nid()
    wf = {
        "nodes": [
            {
                "id": "base-node",
                "type": "base-node",
                "x": 360,
                "y": 2760,
                "properties": {
                    "stepName": "基本信息",
                    "node_data": {
                        "name": args.name,
                        "desc": "",
                        "prologue": args.prologue,
                        "tts_type": "BROWSER",
                        "file_upload_enable": False,
                    },
                    "user_input_field_list": [],
                    "api_input_field_list": [],
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
            {
                "id": sk_id,
                "type": "search-knowledge-node",
                "x": 700,
                "y": 3340,
                "properties": {
                    "stepName": "知识库检索",
                    "condition": "AND",
                    "config": {
                        "fields": [
                            {"label": "分段列表", "value": "paragraph_list"},
                            {"label": "检索结果", "value": "data"},
                        ]
                    },
                    "node_data": {
                        "knowledge_id_list": [args.knowledge_id],
                        "knowledge_setting": {
                            "top_n": 3,
                            "similarity": 0.6,
                            "max_paragraph_char_number": 5000,
                            "search_mode": "embedding",
                        },
                        "question_reference_address": ["start-node", "question"],
                        "show_knowledge": True,
                        "search_scope_type": "custom",
                        "search_scope_source": "knowledge",
                    },
                },
            },
            {
                "id": ai_id,
                "type": "ai-chat-node",
                "x": 980,
                "y": 3340,
                "properties": {
                    "stepName": "AI 对话",
                    "condition": "AND",
                    "config": {
                        "fields": [
                            {"label": "回答", "value": "answer"},
                            {"label": "思考", "value": "reasoning_content"},
                        ]
                    },
                    "node_data": {
                        "model_id": args.model_id,
                        "system": (
                            "【Role】你是企业知识库问答助手，面向内部用户解答已入库文档相关问题。\n"
                            "【限制】仅依据下方检索结果作答；检索为空或无关时说明「未找到依据」，禁止编造；"
                            "不回答与知识库无关的闲聊或越权请求。\n"
                            "【输出】先一句话结论，再列 1～3 条依据（点明检索片段要点）；"
                            "无法回答时只输出：未在知识库中找到相关说明。"
                        ),
                        "prompt": (
                            "【上下文】\n"
                            "检索结果：{{知识库检索.data}}\n"
                            "用户问题：{{开始.question}}\n\n"
                            "【示例】\n"
                            "输入：报销需要哪些材料？\n"
                            "输出：结论：……。依据：1）…… 2）……\n\n"
                            "请按 system 中的 Role、限制与输出约定作答。"
                        ),
                        "dialogue_number": 1,
                        "dialogue_type": "WORKFLOW",
                        "is_result": True,
                        "model_params_setting": {},
                        "model_setting": {"reasoning_content_enable": False},
                    },
                },
            },
        ],
        "edges": [
            {
                "id": e1,
                "type": "app-edge",
                "sourceNodeId": "start-node",
                "targetNodeId": sk_id,
                "sourceAnchorId": "start-node_right",
                "targetAnchorId": f"{sk_id}_left",
                "startPoint": {"x": 0, "y": 0},
                "endPoint": {"x": 0, "y": 0},
                "pointsList": [],
                "properties": {},
            },
            {
                "id": e2,
                "type": "app-edge",
                "sourceNodeId": sk_id,
                "targetNodeId": ai_id,
                "sourceAnchorId": f"{sk_id}_right",
                "targetAnchorId": f"{ai_id}_left",
                "startPoint": {"x": 0, "y": 0},
                "endPoint": {"x": 0, "y": 0},
                "pointsList": [],
                "properties": {},
            },
        ],
    }
    text = json.dumps(wf, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
