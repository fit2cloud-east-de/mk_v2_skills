#!/usr/bin/env python3
"""Create knowledge base: base | web | workflow.

For --kind workflow, by default installs a publish-valid skeleton
(knowledge-base-node + one data-source + split/write chain) so the UI
does not show「基本信息节点必填」/「开始节点必填」on empty graphs.

Usage:
  python create_knowledge.py --kind workflow --name demo --embedding-model-id E --yes
  python create_knowledge.py --kind workflow --skeleton web --name demo --embedding-model-id E --yes
  python create_knowledge.py --kind workflow --no-skeleton ...   # empty work_flow (not recommended)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _lib.knowledge_workflow_graph import (
    minimal_local_ingest_graph,
    minimal_web_ingest_graph,
)
from _lib.maxkb_client import (
    MaxKBError,
    add_common_args,
    client_from_args,
    print_json,
    require_yes,
)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_args(p)
    p.add_argument("--kind", choices=["base", "web", "workflow"], default="base")
    p.add_argument("--name", required=True)
    p.add_argument("--embedding-model-id", required=True)
    p.add_argument("--desc", default="")
    p.add_argument("--folder-id", default=None)
    p.add_argument("--source-url", help="Required for --kind web (Web knowledge, not workflow skeleton)")
    p.add_argument("--selector", default="body")
    p.add_argument(
        "--skeleton",
        choices=["local", "web", "none"],
        default="local",
        help="workflow only: install publish-valid graph (default local). Use none to skip.",
    )
    p.add_argument(
        "--no-skeleton",
        action="store_true",
        help="Alias for --skeleton none (workflow); leaves empty work_flow — UI publish will fail until you save a valid graph",
    )
    args = p.parse_args()
    require_yes(args.yes, f"create knowledge ({args.kind}) {args.name}")

    c = client_from_args(args)
    folder = args.folder_id or c.folder_id()
    body = {
        "name": args.name,
        "folder_id": folder,
        "desc": args.desc,
        "embedding_model_id": args.embedding_model_id,
    }
    if args.kind == "web":
        if not args.source_url:
            p.error("--source-url required for web")
        body["source_url"] = args.source_url
        body["selector"] = args.selector
        path = c.ws("knowledge/web")
    elif args.kind == "workflow":
        path = c.ws("knowledge/workflow")
    else:
        path = c.ws("knowledge/base")

    try:
        created = c.admin("POST", path, json_body=body)
        data = c.data_of(created) or {}
        kid = data.get("id")

        skeleton = "none" if args.no_skeleton else args.skeleton
        if args.kind == "workflow" and kid and skeleton != "none":
            wf = minimal_web_ingest_graph() if skeleton == "web" else minimal_local_ingest_graph()
            saved = c.admin(
                "PUT",
                c.ws(f"knowledge/{kid}/workflow"),
                json_body={"work_flow": wf},
            )
            out = {
                "created": created,
                "skeleton": skeleton,
                "skeleton_saved": saved,
                "hint": (
                    "已写入可发布骨架（含 knowledge-base-node + 数据源 + 写入）。"
                    "可再改节点/导入 .kbwf；勿删掉基本信息固定 id 与全部数据源。"
                ),
            }
            print_json(out)
            return 0

        if args.kind == "workflow" and skeleton == "none":
            print_json(
                {
                    "created": created,
                    "warning": (
                        "未安装骨架：空 work_flow 在界面发布会报「基本信息节点必填」/「开始节点必填」。"
                        "请立即 save_knowledge_workflow 或重新 create 不带 --no-skeleton。"
                    ),
                }
            )
            return 0

        print_json(created)
        return 0
    except MaxKBError as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
