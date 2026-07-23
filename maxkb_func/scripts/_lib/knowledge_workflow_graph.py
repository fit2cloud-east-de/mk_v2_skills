"""Knowledge workflow graph helpers — avoid UI publish errors.

UI (KnowledgeWorkFlowInstance) requires:
  - node id == knowledge-base-node
  - >=1 properties.kind == data-source
  - branches end at knowledge-write-node
"""
from __future__ import annotations

from typing import Any

KB_BASE_ID = "knowledge-base-node"
WRITE_TYPE = "knowledge-write-node"
DATA_SOURCE_KIND = "data-source"
DATA_SOURCE_TYPES = frozenset(
    {
        "data-source-local-node",
        "data-source-web-node",
    }
)

# Stable ids for the default local ingest chain (safe to re-PUT)
LOCAL_ID = "ds-local-001"
EXTRACT_ID = "extract-001"
SPLIT_ID = "split-001"
WRITE_ID = "write-001"
WEB_ID = "ds-web-001"


def knowledge_base_node() -> dict[str, Any]:
    return {
        "id": KB_BASE_ID,
        "type": KB_BASE_ID,
        "x": 80,
        "y": 80,
        "properties": {
            "stepName": "基本信息",
            "config": {
                "fields": [],
                "globalFields": [{"label": "知识库", "value": "knowledge"}],
            },
            "user_input_config": {"title": "文档处理设置"},
            "user_input_field_list": [],
            "node_data": {"name": "", "desc": "", "prologue": "", "tts_type": "BROWSER"},
            "showNode": True,
        },
    }


def _edge(eid: str, src: str, tgt: str) -> dict[str, Any]:
    return {
        "id": eid,
        "sourceNodeId": src,
        "targetNodeId": tgt,
        "sourceAnchorId": f"{src}_right",
        "targetAnchorId": f"{tgt}_left",
    }


def minimal_local_ingest_graph() -> dict[str, Any]:
    """Valid publishable skeleton: base + local → extract → split → write."""
    nodes = [
        knowledge_base_node(),
        {
            "id": LOCAL_ID,
            "type": "data-source-local-node",
            "x": 80,
            "y": 360,
            "properties": {
                "kind": DATA_SOURCE_KIND,
                "stepName": "本地文件",
                "config": {"fields": [{"label": "文件列表", "value": "file_list"}]},
                "node_data": {
                    "file_type_list": [
                        "TXT",
                        "MD",
                        "DOCX",
                        "PDF",
                        "HTML",
                        "CSV",
                        "XLS",
                        "XLSX",
                        "ZIP",
                    ],
                    "file_count_limit": 50,
                    "file_size_limit": 100,
                },
                "showNode": True,
            },
        },
        {
            "id": EXTRACT_ID,
            "type": "document-extract-node",
            "x": 420,
            "y": 360,
            "properties": {
                "stepName": "文档内容提取",
                "config": {
                    "fields": [
                        {"label": "文档内容", "value": "content"},
                        {"label": "文档列表", "value": "document_list"},
                    ]
                },
                "node_data": {"document_list": [LOCAL_ID, "file_list"]},
                "showNode": True,
            },
        },
        {
            "id": SPLIT_ID,
            "type": "document-split-node",
            "x": 760,
            "y": 360,
            "properties": {
                "stepName": "文档分段",
                "config": {"fields": [{"label": "分段列表", "value": "paragraph_list"}]},
                "node_data": {
                    "document_list": [EXTRACT_ID, "document_list"],
                    "split_strategy": "auto",
                    "chunk_size": 256,
                    "chunk_size_type": "custom",
                    "patterns": [],
                    "limit": 4096,
                    "with_filter": False,
                },
                "showNode": True,
            },
        },
        {
            "id": WRITE_ID,
            "type": WRITE_TYPE,
            "x": 1100,
            "y": 360,
            "properties": {
                "stepName": "知识库写入",
                "config": {"fields": []},
                "node_data": {
                    "document_list": [SPLIT_ID, "paragraph_list"],
                    "is_result": True,
                },
                "showNode": True,
            },
        },
    ]
    edges = [
        _edge("e-local-extract", LOCAL_ID, EXTRACT_ID),
        _edge("e-extract-split", EXTRACT_ID, SPLIT_ID),
        _edge("e-split-write", SPLIT_ID, WRITE_ID),
    ]
    return {"nodes": nodes, "edges": edges}


def minimal_web_ingest_graph() -> dict[str, Any]:
    """Valid publishable skeleton: base + web → split → write (no extract)."""
    nodes = [
        knowledge_base_node(),
        {
            "id": WEB_ID,
            "type": "data-source-web-node",
            "x": 80,
            "y": 360,
            "properties": {
                "kind": DATA_SOURCE_KIND,
                "stepName": "Web 站点",
                "config": {"fields": [{"label": "文档列表", "value": "document_list"}]},
                "node_data": {},
                "showNode": True,
            },
        },
        {
            "id": SPLIT_ID,
            "type": "document-split-node",
            "x": 420,
            "y": 360,
            "properties": {
                "stepName": "文档分段",
                "config": {"fields": [{"label": "分段列表", "value": "paragraph_list"}]},
                "node_data": {
                    "document_list": [WEB_ID, "document_list"],
                    "split_strategy": "auto",
                    "chunk_size": 256,
                    "chunk_size_type": "custom",
                    "patterns": [],
                    "limit": 4096,
                    "with_filter": False,
                },
                "showNode": True,
            },
        },
        {
            "id": WRITE_ID,
            "type": WRITE_TYPE,
            "x": 760,
            "y": 360,
            "properties": {
                "stepName": "知识库写入",
                "config": {"fields": []},
                "node_data": {
                    "document_list": [SPLIT_ID, "paragraph_list"],
                    "is_result": True,
                },
                "showNode": True,
            },
        },
    ]
    edges = [
        _edge("e-web-split", WEB_ID, SPLIT_ID),
        _edge("e-split-write", SPLIT_ID, WRITE_ID),
    ]
    return {"nodes": nodes, "edges": edges}


def _is_data_source(node: dict) -> bool:
    props = node.get("properties") or {}
    return props.get("kind") == DATA_SOURCE_KIND or node.get("type") in DATA_SOURCE_TYPES


def precheck_workflow(work_flow: dict) -> list[str]:
    problems: list[str] = []
    nodes = work_flow.get("nodes") or []
    if not isinstance(nodes, list) or not nodes:
        return [
            "work_flow.nodes 为空 → 界面「基本信息节点必填」+「开始节点必填」。"
            "请用 create_knowledge --kind workflow（默认会装骨架）或传入含数据源的图。"
        ]

    base = [n for n in nodes if isinstance(n, dict) and n.get("id") == KB_BASE_ID]
    if not base:
        problems.append(
            "缺少 id='knowledge-base-node' → 界面「基本信息节点必填」。"
            "保存时会自动补上；自建 JSON 时禁止改这个固定 id。"
        )
    elif len(base) > 1:
        problems.append("「基本信息」节点只能有一个（id=knowledge-base-node）")

    sources = [n for n in nodes if isinstance(n, dict) and _is_data_source(n)]
    if not sources:
        problems.append(
            "缺少数据源 → 界面「开始节点必填」。"
            "至少保留本地文件 / Web / 数据源型工具之一（properties.kind='data-source'）。"
        )

    writes = [n for n in nodes if isinstance(n, dict) and n.get("type") == WRITE_TYPE]
    if not writes:
        problems.append(
            f"缺少 type='{WRITE_TYPE}' → 界面「节点不能当做结束节点」。"
            "每条数据源链路终点必须是知识库写入。"
        )
    return problems


def ensure_publish_shape(
    work_flow: dict,
    *,
    fix_base: bool = True,
) -> tuple[dict, list[str]]:
    """
    Mutate-safe: return a copy with knowledge-base-node injected if missing.
    Does NOT invent a data-source (agent/user must choose local/web/tool).
    """
    import copy

    wf = copy.deepcopy(work_flow) if isinstance(work_flow, dict) else {"nodes": [], "edges": []}
    notes: list[str] = []
    nodes = wf.setdefault("nodes", [])
    if not isinstance(nodes, list):
        wf["nodes"] = []
        nodes = wf["nodes"]
        notes.append("nodes 非法，已重置为 []")

    if fix_base and not any(isinstance(n, dict) and n.get("id") == KB_BASE_ID for n in nodes):
        # If someone used type=knowledge-base-node but wrong id, fix id
        fixed = False
        for n in nodes:
            if isinstance(n, dict) and n.get("type") == KB_BASE_ID and n.get("id") != KB_BASE_ID:
                n["id"] = KB_BASE_ID
                notes.append("已修正基本信息节点 id → knowledge-base-node（避免「基本信息节点必填」）")
                fixed = True
                break
        if not fixed:
            nodes.insert(0, knowledge_base_node())
            notes.append("已自动补上固定节点 knowledge-base-node（避免「基本信息节点必填」）")

    return wf, notes
