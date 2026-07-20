---
name: maxkb-v2-workflow
description: >-
  Build/update/debug/publish MaxKB v2 workflows via Python 3.11 scripts/.
  Use for 编排工作流、高级智能体、节点参数、调试、发布. Includes validate_workflow_params.py.
---

# MaxKB v2 Workflow

Python **3.11+**。套件根：[../../SKILL.md](../../SKILL.md)。执行层连接参数见 [../SKILL.md](../SKILL.md) §0（HOST / WORKSPACE / **普通用户** API_KEY，Key 不进 skills）。  
写操作：确认后加 `--yes`。**删除应用默认禁止**，仅当用户明确要求并「确认删除」后才可跑 `delete_app.py`。沙箱：[SANDBOX.md](../SANDBOX.md) · 节点：[nodes-reference.md](nodes-reference.md) · **拓扑少样本**：[topology-samples/README.md](topology-samples/README.md)

## AI 节点提示词（强制）

落地或改写各类 **AI/大模型节点**（`ai-chat-node`、`question-node`、`intent-node`、参数抽取、多模态理解等）时，提示词必须完整，同时包含：

1. **Role（角色）**  
2. **限制（Constraints）**  
3. **输出（Output 格式/约定）**  
4. **示例（Examples，至少 1 组）**

禁止只写「你是助手」等空泛 system。细则与模板见 [nodes-reference.md](nodes-reference.md)「AI 节点提示词规范」。拓扑样本中的短提示词仅为骨架，保存/发布前须按规范补全。


## 智能体拓扑少样本（选型）

设计智能体前，可按场景从 [topology-samples/](topology-samples/) 选拓扑。每个分 md 固定含：**设计思路 / 场景 / 要点**，以及可解析的 `work_flow` JSON（内含 `design_thinking`、`scenarios`、`key_points`）。

| 拓扑 | 文件 | 典型场景 |
|------|------|----------|
| Sequential 串行 | [01-sequential](topology-samples/01-sequential.md) | 标准 RAG、单路径流程 |
| Parallel 并行 | [02-parallel](topology-samples/02-parallel.md) | 多视角同时算再汇总 |
| Loop 循环 | [03-loop](topology-samples/03-loop.md) | 列表逐步处理 |
| Plan 规划分解 | [04-plan-decompose](topology-samples/04-plan-decompose.md) | 先计划再执行 |
| Branch If-Else/Switch | [05-branch-if-else-switch](topology-samples/05-branch-if-else-switch.md) | 意图/条件分流 |
| Merge/Join 汇聚 | [06-merge-join](topology-samples/06-merge-join.md) | 多源结果合并 |
| Retry 重试 | [07-retry](topology-samples/07-retry.md) | 不稳定工具有限次重试 |
| Short-circuit 短路 | [08-short-circuit](topology-samples/08-short-circuit.md) | 高置信早退 |
| Cache Branch 缓存 | [09-cache-branch](topology-samples/09-cache-branch.md) | 热点问法加速 |
| ReAct | [10-react](topology-samples/10-react.md) | 联网问答、工具解题 |
| Self-Plan+Replan | [11-self-plan-replan](topology-samples/11-self-plan-replan.md) | 旅游/项目开放规划 |
| Hierarchical Plan | [12-hierarchical-plan](topology-samples/12-hierarchical-plan.md) | 论文、软件等超长任务 |
| Tree-of-Thought | [13-tree-of-thought](topology-samples/13-tree-of-thought.md) | 多路径推演择优 |
| Graph-of-Thought | [14-graph-of-thought](topology-samples/14-graph-of-thought.md) | 多线索交叉推理 |
| Chain-of-Thought | [15-chain-of-thought](topology-samples/15-chain-of-thought.md) | 轻量分步推理 |
| Adaptive Router | [16-adaptive-router](topology-samples/16-adaptive-router.md) | 按难度选简单/复杂/规划 |
| Throttle 限流 | [17-throttle](topology-samples/17-throttle.md) | 批量处理控并发 |
| Delegation 委派 | [18-delegation](topology-samples/18-delegation.md) | 主从专家子 Agent |
| Agent Sequential | [19-agent-sequential](topology-samples/19-agent-sequential.md) | 检索→分析→写作→审核 |
| Memory Feedback | [20-memory-feedback](topology-samples/20-memory-feedback.md) | 独立记忆回流（≠聊天记录） |

头脑风暴（路径 A）产出设计时，应点名选用上表哪一种（或组合），再进入脚本落地。

## 脚本

| 脚本 | 用途 |
|------|------|
| `list_apps.py` / `get_app.py` / `list_models.py` | 列表 / 详情 / LLM 模型 |
| `create_app.py` | 创建 WORK_FLOW |
| `save_workflow.py` | 保存 `work_flow` |
| `publish_app.py` | **发布**（单应用 / 多 `--app-id` / `--name-prefix` 批量一键发布） |
| `debug_open.py` / `debug_chat.py` | 调试（开会话 / 发消息，两步） |
| **`debug_app.py`** | **一键调试**：open → chat → 评估是否通 / 是否符合预期（可 `--name-prefix` 批量） |
| `create_app_key.py` / `chat_completions.py` | 应用 Key / 生产对话 |
| `build_minimal_rag_workflow.py` | 生成本地 RAG JSON |
| **`validate_workflow_params.py`** | **联调验证关键节点参数** |
| `delete_app.py` | **删除（仅用户明确要求 + 确认删除 + `--yes`）** |

`MAXKB_WORKSPACE` 可用显示名或 UUID。创建前按 [../SKILL.md](../SKILL.md)「资源存放位置」让用户选根目录 / 已有文件夹 / 新建文件夹；`folder_id` 仅在选根目录时用 workspace id。

## 参数校验脚本

```bash
python validate_workflow_params.py --yes
# 默认保留本次创建的应用/工具；仅当用户明确要求清理时再加：--cleanup
```

覆盖：`file_upload_*`、`user_input`→`form_data`/`{{global.x}}`、条件 IF/ELSE、`tool-node` 引用数组、`tool-lib-node` 模板 `{{节点.result}}`、`reply`、发布与调试。

**tool-lib 入参必须用字符串模板**，不要用 `["node-id","field"]`（见 SANDBOX.md）。

## 标准流水线

```bash
python create_app.py --name "客服助手" --yes
python build_minimal_rag_workflow.py --knowledge-id KID --model-id MID --out /tmp/wf.json
python save_workflow.py --app-id APP --workflow-json /tmp/wf.json --yes
python debug_open.py --app-id APP
python debug_chat.py --chat-id CHAT --message "你好" --no-stream
# 一键调试（推荐）：开会话+提问+评估
python debug_app.py --app-id APP --message "你好" --min-chars 5 --yes
python debug_app.py --name-prefix "[拓扑审核]" --message "请用一句话介绍你自己" --yes
python publish_app.py --app-id APP --yes
# 批量一键发布：python publish_app.py --name-prefix "[拓扑审核]" --yes
```
