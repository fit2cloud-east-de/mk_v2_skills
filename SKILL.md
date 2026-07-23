---
name: mk-v2-skills
description: >-
  MaxKB v2 技能套件根入口。会话开始须先让用户选沟通模式（编程小白/专业），
  再确认本机 Python（≥3.7，跑脚本需 3.11），再选头脑风暴或直接制作，并索取 HOST/WORKSPACE/普通用户 API Key。
  Use for MaxKB、智能体、知识库、工具、头脑风暴、Python 环境、调试发布。
---

# mk_v2_skills（套件根）

本目录是 **Agent Skills 套件根**。安装/路由请指向这里（`mk_v2_skills/`）。

```text
mk_v2_skills/
├── SKILL.md                      ← 本文件：沟通模式 + Python + 路径二选一 + 总路由
├── maxkb_func/                   ← 执行层：脚本落地 MaxKB（需 Python ≥ 3.11）
└── superpowers-6.1.1/            ← 规划层：路径 A 时走头脑风暴（brainstorming）
    └── skills/brainstorming/
```

---

## 0. 会话开场（强制，按顺序）

每次新会话、或用户提出「做智能体 / 知识库 / 工具 / 改编排」时，**按下面顺序**处理。  
未完成 **0.0 沟通模式** 前，不要用专业黑话开场。  
未完成 **0.1 Python 环境** 前，禁止安装依赖、禁止跑 `maxkb_func` 脚本。  
未完成 **0.2 路径 + 连接** 前，禁止写操作（`--yes`）。

### 0.0 沟通模式（最先问用户）

**必须让用户二选一**，本会话锁定为 `MK_AUDIENCE`，后续所有解释、确认文案、报错说明都按该模式调整。

#### 向用户展示的引导文案（可原样使用）

> 凡 A/B/C 或 1/2/3 多选：须按 [maxkb_func/SKILL.md](maxkb_func/SKILL.md)「方案 / 选项展示规范」展开每个选项的具体内容，禁止只甩字母。

```markdown
开始前请先选择本次沟通模式（直接回复 **小白** 或 **专业**）：

### 1. 编程小白（新手）
- **是什么**：你不太会编程，主要懂业务；我会用大白话说明
- **适合**：业务同学、第一次用 MaxKB
- **你会得到**：少术语、生活类比、一步步「点哪里」指引
- **代价或注意**：专业细节会藏在后层，需要时再展开

### 2. 专业模式
- **是什么**：你熟悉编程与 API；结论优先、可直接给命令
- **适合**：开发 / 实施同学
- **你会得到**：节点类型、脚本参数、错误码等专业表述
- **代价或注意**：默认假设你能读脚本与 api-reference
```

#### 模式约定（Agent 必须遵守）

| `MK_AUDIENCE` | 用户画像 | 回答风格 |
|---------------|----------|----------|
| **novice（编程小白）** | 不会编程、只懂业务 | 通俗易懂；先说「要达成什么业务效果」；术语首次出现用括号解释；少贴大段 JSON，必要时说明「这段给系统用的，你一般不用改」；确认/风险用业务语言 |
| **pro（专业模式）** | 会编程 | 偏专业化；可用节点 `type`、CLI、HTTP、拓扑名；默认假设读者能读脚本与 api-reference |

补充规则：

- **小白**：跑脚本前用一句话说明「我接下来会在电脑上执行一条命令帮你完成 xxx」；失败时先说影响（建库没成功），再给可选下一步，避免堆栈原文吓到用户（可折叠/摘要）。  
- **专业**：可直接给命令、路径、字段名；失败可引用 biz `code` / 关键日志。  
- **未选择时**：再问一次，**不要默认**；若用户说「都行」，按 **小白** 处理并告知。  
- 拓扑样本、节点名对小白应译成「先检索再回答」「多路一起查再合并」等说法，需要时再给出专业名。

---

### 0.1 本机 Python 环境

#### Agent 先自行探测（只读，勿擅自装软件）

在终端尝试（按环境选，可多试几个）：

```bash
# 版本
py -0p 2>/dev/null || true
py -3.11 --version 2>/dev/null || true
python3.11 --version 2>/dev/null || true
python3 --version 2>/dev/null || true
python --version 2>/dev/null || true

# 对应 pip（示例）
py -3.11 -m pip --version 2>/dev/null || true
python3.11 -m pip --version 2>/dev/null || true
python3 -m pip --version 2>/dev/null || true
pip3 --version 2>/dev/null || true
```

Windows 还可：`where py`、`where python`、`where pip`。

**版本要求：**

| 用途 | 要求 |
|------|------|
| 探测「本机有没有 Python」 | **≥ 3.7** 即视为「有环境」 |
| 跑本套件 `maxkb_func` 脚本 | **必须 ≥ 3.11**（客户端硬性检查） |
| 推荐 | **3.11.x** |

#### 探测后与用户确认（必问；措辞随 MK_AUDIENCE）

**情况 A — 未找到可用 Python，或仅有 &lt; 3.11（无法跑脚本）**

- **小白文案示例：**

```markdown
我这边还没法在你电脑上自动操作 MaxKB（缺少可用的 Python 3.11 运行环境，探测结果：{简述}）。

需要先安装 Python 3.11（一套常用的小工具运行环境）。是否由我协助安装？
- 回复「确认安装」→ 我再告诉你将执行什么，并一步步带你完成
- 回复「自行安装」→ 你装好后告诉我即可
- 回复「取消」→ 我们仍可以先聊需求、画方案，但暂时不能真的在系统里创建智能体/知识库
```

- **专业文案示例：**

```markdown
未检测到 Python 3.11+（探测：{简述}）。本套件 scripts 硬性要求 ≥3.11。
是否协助安装 Python 3.11？回复「确认安装」/「自行安装」/「取消」。
```

用户确认安装后，Agent 才可执行安装（示例，按 OS 选一种，执行前再贴给用户看一眼）：

- Windows：`winget install Python.Python.3.11` 或引导官网安装包  
- macOS：`brew install python@3.11`  
- Linux：按发行版（如 `sudo apt install python3.11 python3.11-venv`）

装完后重新探测，并进入「情况 B」锁定唤出方式。

**情况 B — 已有 Python ≥ 3.7（含已有 3.11+）**

- **小白**：请用户确认「用哪一个」时，避免只甩路径；可说「一般选带 3.11 的那一项」，并询问是否同意使用探测到的默认项。  
- **专业**：直接请提供 interpreter / pip 唤出方式或绝对路径。

```markdown
本机检测到 Python 环境（探测摘要）：
{列出找到的命令及 version}

跑 MaxKB 脚本需要 **3.11+**。请确认本次会话使用哪一套：

1. **Python 唤出方式或完整路径**（例：`py -3.11` / `python3.11` / 绝对路径）
2. **pip 唤出方式**（推荐：`同一解释器 -m pip`）

也可回复「改用新装 3.11」。
```

#### 锁定后的会话约定（必须遵守）

| 会话变量（概念） | 含义 |
|------------------|------|
| `MK_AUDIENCE` | `novice` \| `pro` |
| `MK_PYTHON` | 如 `py -3.11` |
| `MK_PIP` | 如 `py -3.11 -m pip` |

之后脚本命令一律用锁定的 `MK_PYTHON`（或 venv）。  
路径 A（仅头脑风暴、不跑脚本）可在 Python 未就绪时继续；**一旦要落地必须先完成 0.1**。

---

### 0.2 路径二选一 + MaxKB 连接信息

Python 事宜谈妥后（或用户选择「先只头脑风暴」），用下面文案询问（可按 MK_AUDIENCE 改写措辞，选项含义不变）。  
**未选定路径、且尚未拿到连接三项时，禁止写操作脚本。**

#### 向用户展示的引导文案（可原样使用）

> 选项须展开具体内容（见执行层「方案 / 选项展示规范」）。

```markdown
请选一条工作路径，并提供 MaxKB 连接信息（回复 **A** 或 **B**，并附上三项连接）：

### A. 先头脑风暴（推荐：目标还不清晰时）
- **是什么**：先一起把目标、边界、方案对比想清楚，再动手建资源
- **适合**：「帮我做一个客服助手」这类需求还模糊、要不要知识库/工具未定
- **你会得到**：书面设计（角色、知识库、拓扑、验收问句）后再落地
- **代价或注意**：落地前多一轮确认；获批前不会在系统里创建资源

### B. 直接制作
- **是什么**：目标已明确，现在就去系统里建知识库 / 智能体 / 工具
- **适合**：已有设计文档，或只改开场白、挂已有库等小改
- **你会得到**：更快看到系统里的成品
- **代价或注意**：若需求中途大变，可能要返工

## 连接信息（三项都要）
1. 地址 HOST（浏览器打开 MaxKB 时的网址）
2. 工作空间名称或 ID
3. API Key（普通用户 Key，不要用管理员 Key）

密钥只用于本次会话，不会写入 skill / 仓库。
```

也可与 0.0 / 0.1 **合并成一次消息**问完（模式 + Python + 路径 + 连接），但仍须等用户答完再往下走。

#### Agent 收到回复后怎么走

| 用户选择 | Agent 动作 |
|----------|------------|
| **A 先头脑风暴** | 打开并遵循 [superpowers-6.1.1/skills/brainstorming/SKILL.md](superpowers-6.1.1/skills/brainstorming/SKILL.md)；表达随 `MK_AUDIENCE`；**设计获批前禁止** `maxkb_func` 写操作。 |
| **B 直接制作** | 确认 `MK_PYTHON`≥3.11 → [maxkb_func/SKILL.md](maxkb_func/SKILL.md)；解释深度随模式。 |
| 未选路径 / 未选模式 | 再问，不默认（模式「都行」→ 小白）。 |
| 缺连接三项 | 可先做 A 的澄清，**落地前必须补齐**。 |
| Python 未锁定 / &lt;3.11 | 禁止跑脚本；回到 0.1。 |

#### 何时建议选 A / B（可顺带告知用户）

| 更适合 A（头脑风暴） | 更适合 B（直接制作） |
|----------------------|----------------------|
| 「帮我做一个客服助手」这类目标模糊 | 「用已有 FAQ PDF 建库 + RAG」目标清楚 |
| 要不要知识库/工具/多 Agent 未定 | 只改 prologue、加 reply、调检索参数 |
| 需要 2～3 种方案对比与验收标准 | 已有设计文档 / 上次会话已定稿 |

---

## 1. 头脑风暴（路径 A）

路径 A 时打开 [superpowers-6.1.1/skills/brainstorming/SKILL.md](superpowers-6.1.1/skills/brainstorming/SKILL.md)，把模糊需求澄清成可落地的设计（目的、边界、方案对比、验收场景）。

| 能力 | 说明 |
|------|------|
| **何时用** | 用户选了路径 A，或新做/大改智能体、知识域、工具契约 |
| **何时不用** | 用户选了路径 B；或纯运维小改 |
| **获批后怎么落地** | **不要**再走 `writing-plans` → TDD → worktree；改为打开 **`maxkb_func`** 用脚本落地 |

同目录下其它 skill（TDD、worktree、code review 等）与 MaxKB 编排无关，**默认不要启用**。

### 操作步骤（路径 A）

严格按 [brainstorming/SKILL.md](superpowers-6.1.1/skills/brainstorming/SKILL.md) 的 checklist，并结合 MaxKB 语境：

1. **探索上下文** — 看用户是否已有知识库/应用/文档；勿编造实例上的资源 ID。  
2. **逐个提问** — 一次只问一个问题；优先多选题。建议覆盖：  
   - 用户是谁、解决什么问题  
   - 是否需要知识库、文档从哪来  
   - 是否需要自定义工具（以及能否用工作流内 `tool-node`）  
   - 成功标准 / 3～5 条验收问句  
   - 拒答与安全边界  
   - **资源放哪里**：工作区根目录 / 已有文件夹 / 新建文件夹（落地前再确认一次）  
3. **给 2～3 种方案（必须展开正文）** — 例如「纯 RAG / RAG+工具 / 无知识库仅工具」。  
   **禁止**只写「A / B / C」或一行标题就让用户选。按执行层 [maxkb_func/SKILL.md](maxkb_func/SKILL.md)「方案 / 选项展示规范」：每个方案用卡片写清 **是什么 / 适合 / 你会得到 / 代价 / 接下来我会做**，推荐项置顶并说明理由。  
   **智能体拓扑**从 [topology-samples](maxkb_func/maxkb-v2-workflow/topology-samples/README.md) 选型时同样展开（Sequential / Parallel / ReAct / Plan… 各自业务含义）。  
4. **分段呈现设计并请用户确认** — 按块确认（角色与边界 → 知识库 → **拓扑类型** → 工作流节点 → **各 AI 节点提示词（Role/限制/输出/示例）** → 工具 → 验收）。  
5. **写入设计文档（可选但推荐）** — 可存到会话约定目录，例如 `docs/maxkb-specs/YYYY-MM-DD-<topic>-design.md`；**禁止写入真实 API Key / 完整 HOST 密钥**。  
6. **自检** — 无占位符、无矛盾、范围清晰。  
7. **用户确认书面设计**。  
8. **交接落地**（获批后进执行层，不要再走 writing-plans）：  
   - 确认会话已锁定 **Python ≥ 3.11**（§0.1）  
   - 打开 [maxkb_func/SKILL.md](maxkb_func/SKILL.md)  
   - 用开场已收集的 HOST / WORKSPACE / API_KEY  
   - 按下方「交接清单」用 `{MK_PYTHON}` 执行脚本；写操作先确认再 `--yes`

### 头脑风暴 → maxkb_func 交接清单

设计获批后，落地前整理成短清单（可写在回复里）：

```markdown
## MaxKB 落地 tasks
- [ ] 存放位置（必选其一）：**根目录** / **已有文件夹**（名称或 id） / **新建文件夹**（名称）
- [ ] 知识库：是/否；类型 base|web|workflow；文档类型（DOCX→普通分段 / PDF→是否 MinerU）；检索模式 embedding|keywords|blend
- [ ] 工具：无 / tool-node 内嵌 / 工具库 tool-lib
- [ ] 智能体：名称；开场白；**拓扑类型**（见 topology-samples，如 sequential / react / delegation）
- [ ] 主要节点链（对照所选拓扑 JSON）
- [ ] **AI 节点提示词**：每个大模型节点均含 Role / 限制 / 输出 / 示例（见 workflow/nodes-reference）
- [ ] 验收问句：（3～5 条）
- [ ] 连接：HOST / WORKSPACE / 普通用户 API_KEY（已收集则直接用，勿写入文件）
- [ ] Python：本会话已确认的 MK_PYTHON / MK_PIP（≥3.11）
- [ ] 沟通模式：小白(novice) / 专业(pro) — 后续解释按此模式
```

然后进入 `maxkb_func`：建库 → 入库 → 建应用/存工作流 → 调试 → 发布（按需）。  
**创建任何资源前**须确认存放位置（见 `maxkb_func`「资源存放位置」）：根目录无需建文件夹；或选已有文件夹；或先新建文件夹再创建。

---

## 2. maxkb_func（执行层）

详见 [maxkb_func/SKILL.md](maxkb_func/SKILL.md)。一律使用 §0.1 锁定的解释器；对用户说明深度遵循 §0.0 `MK_AUDIENCE`。

| 意图 | 打开 |
|------|------|
| 工作流 / 调试 / 发布 | [maxkb_func/maxkb-v2-workflow/SKILL.md](maxkb_func/maxkb-v2-workflow/SKILL.md) |
| **智能体拓扑少样本（串行/并行/ReAct/…）** | [maxkb_func/maxkb-v2-workflow/topology-samples/README.md](maxkb_func/maxkb-v2-workflow/topology-samples/README.md) |
| 知识库 | [maxkb_func/maxkb-v2-knowledge/SKILL.md](maxkb_func/maxkb-v2-knowledge/SKILL.md) |
| 工具与沙箱 | [maxkb_func/maxkb-v2-tools/SKILL.md](maxkb_func/maxkb-v2-tools/SKILL.md) |
| 端到端示例 | [maxkb_func/examples.md](maxkb_func/examples.md) |

路径 B 或路径 A 设计获批后，都走这里。

---

## 3. 硬约束（全套件）

1. **沟通模式**：开场必选「编程小白 / 专业」；锁定 `MK_AUDIENCE`；未选不默认（「都行」→ 小白）。全程按模式调整表述深度。  
2. **Python**：先探测再问用户；无 3.11+ 须用户确认后才可协助安装；锁定后本会话只用该 `MK_PYTHON`/`MK_PIP`。跑脚本硬性 **≥ 3.11**。  
3. **密钥**：普通用户 API Key；禁止管理员 Key；禁止写入 skill / `.env` / 示例 / 设计文档。只用 `--host` / `--workspace` / `--api-key` 或当次进程环境变量。  
4. **写操作**：人工确认 + `--yes`；见 [maxkb_func/AUTH_AND_SAFETY.md](maxkb_func/AUTH_AND_SAFETY.md)。  
5. **删除资源**：默认禁止通过 API/脚本删除任何资源（应用、知识库、文档、工具、Key 等）。**仅当用户明确要求删除**，并经「确认删除」二次确认 + `--yes` 后才可执行；禁止测试后顺手清理、禁止隐式删除。详见 AUTH §4。  
6. **AI 节点提示词**：凡 `ai-chat-node` 等大模型节点，落地提示词必须完整包含 **Role / 限制 / 输出 / 示例**；禁止空泛「你是助手」。见 [maxkb_func/maxkb-v2-workflow/nodes-reference.md](maxkb_func/maxkb-v2-workflow/nodes-reference.md)。  
7. **规划产物**：可写规格与 tasks，勿写真实密钥。  
8. **头脑风暴获批后**：进入 `maxkb_func` 落地；不要改写 `superpowers-6.1.1/` 下的文件来「适配」本套件。  
9. **路径未选清时不要默认直接制作**；小改若用户明确说「直接做」可走 B。
