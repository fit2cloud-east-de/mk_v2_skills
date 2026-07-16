---
name: maxkb-func
description: >-
  MaxKB v2 执行层：通过 Bearer API Key 与 Python 3.11+ 脚本编排工作流、知识库与工具。
  进入本层前须完成套件根 §0：沟通模式（小白/专业）、Python、路径 A/B、HOST/WORKSPACE/普通用户 API Key。
  Prefer scripts/. Use for MaxKB 落地、调试、发布、sandbox。
---

# maxkb_func（MaxKB 执行层）

上级套件根：[../SKILL.md](../SKILL.md)。

**优先跑 `scripts/`（Python ≥ 3.11）。禁止把真实 API Key 写入本仓库任何 skill / 文档 / 示例文件。**  
**禁止使用项目级 `.env`**：请用 `--host` / `--workspace` / `--api-key`（或当次进程环境变量）传入连接信息。  
**解释器**：一律使用套件根 §0.1 已与用户确认的 `MK_PYTHON` / `MK_PIP`（或由其创建的 `.venv311`）。  
**表述**：遵循套件根 §0.0 `MK_AUDIENCE`（小白通俗 / 专业技术）。  
**AI 节点**：编排工作流时提示词须含 Role / 限制 / 输出 / 示例，见 [maxkb-v2-workflow/nodes-reference.md](maxkb-v2-workflow/nodes-reference.md)。

## 0. 进入本层前：模式 + Python + 路径 + 连接

若本会话**尚未**在套件根完成开场，Agent 必须先按 [../SKILL.md](../SKILL.md) §0 处理，摘要如下：

### 0.0 沟通模式

先问用户选 **编程小白** 或 **专业模式**，锁定 `MK_AUDIENCE=novice|pro`。未选不往下用专业黑话开场。

### 0.1 Python（先于脚本）

1. 探测本机是否有 Python（≥3.7 算「有」；**跑本目录脚本必须 ≥3.11**）。  
2. 没有 3.11+ → 询问用户是否确认协助安装 Python 3.11；未确认不得擅自安装。  
3. 已有环境 → 请用户提供 Python / pip 的**唤出命令或完整路径**，本会话锁定为 `MK_PYTHON` / `MK_PIP`。  
4. 未锁定 3.11+ 前：**禁止** `pip install`、禁止跑本目录任何脚本。

### 0.2 路径 + 连接（可与上文同条消息）

```markdown
请选一条工作路径，并提供 MaxKB 连接信息：

## 路径（二选一）
A. **先头脑风暴** — 需求不清，先想清楚再动手  
B. **直接制作（本执行层）** — 目标已明确，现在就建库/智能体/工具

## 连接信息（三项都要）
1. 地址 HOST
2. 工作空间名称或 ID
3. API Key（普通用户 Key，不要用管理员 Key）

密钥只用于本次会话参数传入，勿写入仓库。
```

| 选择 | 动作 |
|------|------|
| **A** | **先不要在本层写操作**；回到套件根做 brainstorming；获批后再回本层（仍须 MK_PYTHON≥3.11）。 |
| **B** | `MK_PYTHON` 已是 3.11+ 且收齐连接三项后继续。 |
| 用户说「已头脑风暴完 / 设计已批」 | 视为可直接制作；仍须 Python + 连接三项。 |

连接三项含义：

| 参数 | 含义 | 示例形态（仅形状，勿抄真实值） |
|------|------|------------------------------|
| **HOST** | MaxKB 访问地址 | `https://your-maxkb.example.com` |
| **WORKSPACE** | 工作空间显示名或 UUID | `MyWorkspace` 或 UUID |
| **API_KEY** | **普通用户**头像 → API Key 管理 | 常以 `user-` 开头 |

### Key 选用规则

- **要用**：普通用户系统 API Key → `/admin/api/**`  
- **不要用**：管理员 / 超管 Key  
- **另外**：生产对话再用应用 `agent-...` Key  

```bash
# 将 {MK_PYTHON} 换成用户确认的解释器，例如 py -3.11 或 python3.11
{MK_PYTHON} scripts/list_workspaces.py \
  --host https://your-maxkb.example.com \
  --workspace MyWorkspace \
  --api-key YOUR_USER_KEY
```

**永远不要**把真实 Key 写进 `SKILL.md`、`*.md`、示例、`.env` 或提交内容。

## 环境准备

在本目录 `maxkb_func/` 下，用**已锁定**的解释器：

```bash
{MK_PYTHON} -m venv .venv311
# Windows
.venv311\Scripts\python.exe -m pip install -r scripts/requirements.txt
# Unix
.venv311/bin/python -m pip install -r scripts/requirements.txt
```

此后优先用 venv 内 python 跑脚本。不创建项目 `.env`。

客户端会把 HTTP 200 但业务 `code≠200` 当失败抛出。

## 强制安全门禁

写操作加 `--yes`；先向用户确认并说明风险。见 [AUTH_AND_SAFETY.md](AUTH_AND_SAFETY.md)。

**删除硬约束（默认禁止）**：用户未明确要求时，**禁止**通过 API 或 `delete_*.py` 删除任何资源（含联调后的「顺手清理」）。仅当用户明确要求删除，并经「确认删除」+ `--yes` 后才可执行。详见 AUTH §4。

## 沙箱（工具必读）

默认禁止 subprocess；`markitdown` 等依赖 shell 的库不可用。见 [SANDBOX.md](SANDBOX.md)。

## 任务路由

| 意图 | 打开 |
|------|------|
| 工作流 | [maxkb-v2-workflow/SKILL.md](maxkb-v2-workflow/SKILL.md) |
| 拓扑少样本 | [maxkb-v2-workflow/topology-samples/README.md](maxkb-v2-workflow/topology-samples/README.md) |
| 知识库 | [maxkb-v2-knowledge/SKILL.md](maxkb-v2-knowledge/SKILL.md) |
| 工具 | [maxkb-v2-tools/SKILL.md](maxkb-v2-tools/SKILL.md) |
| 示例 | [examples.md](examples.md) |
| 套件总路由 / Python 开场 | [../SKILL.md](../SKILL.md) |

## 约定

1. 无复用工具 → `tool-node`；通用 → `create_tool.py` + `tool-lib-node`（见 SANDBOX）
2. 无向量模型时无法建库，需有权限账号先配置模型
3. `folder_id` 默认等于 workspace id
4. **密钥永不入库；不用项目 `.env`**
5. 从头脑风暴交接过来时，按根 SKILL 的「落地 tasks」清单执行，并用验收问句做 `debug_chat` / `hit_test`
6. **本会话只用用户确认的 Python/pip（或 venv），不要换来换去**
7. **对用户说明遵循 MK_AUDIENCE（小白通俗 / 专业技术）**
