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

## 方案 / 选项展示规范（强制）

凡让用户在 **A/B/C（或 1/2/3）** 中选择时，**禁止只甩字母或标题**。必须把每个选项的具体内容完整写进同一条消息，用户不点开别处也能看清再选。

推荐卡片模板（可按 `MK_AUDIENCE` 改措辞，结构保留）：

```markdown
请选择方案（直接回复 **A / B / C** 即可）：

### A. 〈方案短名〉（推荐）
- **是什么**：一句话说明会做成什么样  
- **适合谁 / 什么场景**：…  
- **你会得到**：…（结果/能力）  
- **代价或注意**：…（时间、权限、效果风险等）  
- **接下来我会做**：…（落地步骤摘要，3 条内）

### B. 〈方案短名〉
- **是什么**：…
- **适合谁 / 什么场景**：…
- **你会得到**：…
- **代价或注意**：…
- **接下来我会做**：…

### C. 〈方案短名〉
- …
```

硬性要求：

1. **每个选项至少 3～5 行实质内容**（是什么 / 适合 / 代价）；不要「A. 根目录 / B. 已有文件夹」这种一行完事。  
2. **推荐项写在最前**，并标明「推荐」及一句理由。  
3. 需要列表数据（已有文件夹、模型、知识库）时：**先列出具体名称/摘要**，再让用户选编号；勿说「请选已有文件夹」却不展示列表。  
4. 小白模式：少术语；专业模式：可加 `kind` / 脚本名，但仍须保留可读说明。

适用范围：沟通模式、路径 A/B、资源存放位置、知识库类型、PDF/MinerU、头脑风暴 2～3 种架构方案、拓扑选型等一切多选确认。

## 资源存放位置（创建前必问）

创建**智能体 / 知识库 / 工具**前，**必须让用户三选一**，勿默认塞进根目录却不告知。按上方「方案展示规范」展开，例如：

```markdown
资源放在哪里？（回复 **1 / 2 / 3**）

### 1. 根目录（推荐：试玩 / 不想多建目录时）
- **是什么**：资源直接建在当前工作区根下，不再套一层文件夹  
- **适合**：临时联调、只有少数几个智能体/知识库  
- **你会得到**：创建后在工作区根目录列表里就能看到  
- **代价或注意**：资源一多会显得乱，后期想归类要再搬家  
- **接下来我会做**：用工作区 id 作为 `folder_id` 直接创建（不新建文件夹）

### 2. 已有文件夹
- **是什么**：放进你空间里已经存在的某个文件夹  
- **适合**：已有「客服」「产品手册」等分类，想和现有资源放一起  
- **你会得到**：和新旧资源同一目录，界面更好找  
- **代价或注意**：需要你告诉我文件夹名称或从我列出的清单里选编号  
- **接下来我会做**：先列出该类型（智能体/知识库/工具）下的文件夹，请你选定后再创建

### 3. 新建文件夹
- **是什么**：先建一个新文件夹，再把资源放进去  
- **适合**：新项目/新业务线，想从干净目录开始  
- **你会得到**：独立目录，名称由你定  
- **代价或注意**：新建文件夹需要对应权限；若 403，请你在界面先建好再改选「已有文件夹」  
- **接下来我会做**：按你给的名称创建文件夹，再在其中创建资源
```

| 选择 | 做法 |
|------|------|
| 根目录 | `folder_id` = workspace id（`c.folder_id()`），**不**调用建文件夹 |
| 已有文件夹 | `list_folders.py --source APPLICATION\|KNOWLEDGE\|TOOL` → **先展示列表** → 用户选定 → 创建脚本传 `--folder-id` |
| 新建文件夹 | `create_folder.py --source … --name … --yes` → 用返回的文件夹 id 作为 `--folder-id` |

**权限说明**：列出文件夹普通用户一般可用；**新建文件夹**需要工作区对应该源的文件夹创建权限（或工作区管理员）。若 API 返回 `403 无权限访问`，请用户在 MaxKB 界面建好文件夹后选「已有文件夹」，或换有权限的账号。

智能体 / 知识库 / 工具 的文件夹是**分源**的（`APPLICATION` / `KNOWLEDGE` / `TOOL`），同名文件夹在不同源下是不同资源。

文件夹 API 路径源段为**大写**：`/workspace/{WS}/APPLICATION/folder`（勿用小写 `application`）。

## 约定

1. 无复用工具 → `tool-node`；通用 → `create_tool.py` + `tool-lib-node`（见 SANDBOX）
2. 无向量模型时无法建库，需有权限账号先配置模型
3. **`folder_id`：按用户选择**；仅当用户明确选「根目录」时才用 workspace id；创建脚本传 `--folder-id`
4. **密钥永不入库；不用项目 `.env`**
5. 从头脑风暴交接过来时，按根 SKILL 的「落地 tasks」清单执行，并用验收问句做 `debug_chat` / `hit_test`
6. **本会话只用用户确认的 Python/pip（或 venv），不要换来换去**
7. **对用户说明遵循 MK_AUDIENCE（小白通俗 / 专业技术）**
8. 文件夹脚本：`scripts/list_folders.py`、`scripts/create_folder.py`
