---
name: maxkb-v2-knowledge
description: >-
  MaxKB knowledge scripts (Python 3.11+): create base/web/workflow KB, ingest,
  hit_test; doc-type selection (DOCX vs PDF/MinerU), kbwf import, split norms.
  Use for 知识库、向量模型、分段入库、类型选型、MinerU、PDF.
---

# MaxKB v2 Knowledge

写操作加 `--yes`。套件根：[../../SKILL.md](../../SKILL.md)。启动前先完成执行层 [../SKILL.md](../SKILL.md) §0（普通用户 Key、沟通模式、Python，勿写入 skills）。  
**删除默认禁止**：未获用户明确要求时，禁止跑 `delete_knowledge.py` 或调用删除/批量删除接口。  
API 对照：[api-reference.md](api-reference.md)。  
入库中间数据形状（工具/`AI` 输出硬约束）：**[ingest-io-contracts.md](ingest-io-contracts.md)**。  
表述深度遵循 `MK_AUDIENCE`。

## 注意

- `MAXKB_WORKSPACE` 可用显示名，客户端解析为 UUID。
- 部分环境下 `GET .../knowledge/embedding_model` 可能报「用户 ID 必填」→ `list_embedding_models.py` 会回退 `model_list`。
- 若 workspace **没有向量模型**，建库会失败，需有权限的账号先配置 EMBEDDING 模型。
- 建库前先 `list_embedding_models.py`，把返回的 `id` 作为 `--embedding-model-id`。
- **禁止静默覆盖**：`import_knowledge_workflow.py` 会覆盖目标库的入库工作流；默认只导入到**新建**的 workflow 库（见 §1.2）。

---

## 1. 知识库类型选型规则

MaxKB v2 常用三类（`create_knowledge.py --kind`）：

| kind | 名称 | 数据从哪来 | 何时选 | 何时不要选 |
|------|------|------------|--------|------------|
| **base** | 通用/文档知识库 | 本地上传 → split → batch_create | **默认首选**：DOCX/MD/TXT、FAQ、制度等「文本可直接切」的文档 | 主源为复杂 PDF（版式/扫描/双栏）且要用 MinerU；或需自定义入库流水线 |
| **web** | Web 知识库 | `source_url` + 可选 CSS `selector`，可 sync | 官网帮助中心、公开文档站、需定期同步网页 | 页面强登录墙/反爬；内容主要是本地文件；结构极不稳定 |
| **workflow** | 工作流知识库 | 库内编排：数据源→解析→分段→写入 | **PDF + MinerU 模板**；多源清洗；通用 base「上传即分」不够用 | 简单 DOCX/MD「传几个文件」——用 base 更省事 |

### 1.1 按文档类型选型（Agent 必循）

| 文档类型 | 推荐 kind | 入库方式 | 说明（须向用户讲清） |
|----------|-----------|----------|----------------------|
| **DOCX / DOC** | **base** | 普通 `split` → `batch_create` / `ingest_file` | Word 抽出文本质量通常够用，**优先普通分段**，不必上 MinerU |
| **MD / TXT / RTF** | **base** | 同上 | 纯文本，普通分段即可 |
| **XLSX / CSV / 表格** | **base** | 表格/QA 文档接口（见 api-reference） | 不要当纯文本乱切 |
| **FAQ 问答对** | **base** | QA 上传或按问答切段 | 见 §3.2 |
| **PDF** | 默认建议 **workflow + MinerU** | 见 §1.2 | 直接对 PDF 做 `document/split` 常出现：乱序、双栏串行、表格碎裂、公式/页眉噪声 → **检索命中差**。MinerU 先结构化成 Markdown（可保留图文）再分段，效果通常明显更好 |
| **扫描件 PDF / 复杂版式 PDF** | **强烈建议 MinerU** | §1.2 | 普通分段几乎不可用 |
| **网页** | **web** | sync | 非 PDF 场景 |

**PDF 必做确认（不可跳过）**：出现 PDF 入库需求时，Agent 必须先用通俗话解释原因，再请用户明确选择。  
按 [../SKILL.md](../SKILL.md)「方案 / 选项展示规范」展开（禁止只写「1.MinerU 2.普通分段」）：

```markdown
这份 PDF 怎么入库？（回复 **1 / 2**）

### 1. MinerU 方案（推荐）
- **是什么**：先用 MinerU 把 PDF 解析成结构更好的 Markdown（版式、表格、双栏更友好），再写入「工作流知识库」
- **适合**：扫描件、复杂版式、表格多、双栏、公式/页眉干扰多的 PDF
- **你会得到**：通常检索命中更好、段落更干净；库类型为可编排的工作流知识库
- **代价或注意**：步骤比「直接上传」多；在线 MinerU 不适合敏感文档（可选本地 MinerU）
- **接下来我会做**：新建工作流知识库 → 导入 MinerU 模板 → 配参 → **自动调试** → 发布

### 2. 仍用普通分段
- **是什么**：当普通文档库，直接对 PDF 做分段入库
- **适合**：纯文字、版式极简单、你能接受检索效果可能偏差
- **你会得到**：更快建好；步骤少
- **代价或注意**：乱序、表格碎裂、页眉噪声常见 → **命中可能变差**
- **接下来我会做**：建通用知识库 → `ingest_file` / split 入库（并在回复中再次提醒风险）
```

未得到用户确认前，**不要**下载模板、建库或导入工作流。

向用户二次确认在线 vs 本地 MinerU 时，同样用完整卡片展开（敏感文档不要引导上在线 MinerU）。

### 1.2 PDF → MinerU 工作流模板（确认后执行）

商店页（给人看）：

| 场景 | 商店入口 | preset（脚本） |
|------|----------|----------------|
| **一般非敏感** PDF，可用在线解析 | [kbwf-mineru-pdf-rag](https://apps.fit2cloud.com/maxkb/kbwf-mineru-pdf-rag) | `mineru-pdf-rag` |
| **敏感/内网**，本地 MinerU Gradio | [kbwf-mineru-local-markdown](https://apps.fit2cloud.com/maxkb/kbwf-mineru-local-markdown) | `mineru-local-md` |

向用户二次确认选哪条（在线 vs 本地）；敏感文档不要引导上在线 MinerU。

#### 防覆盖规则（硬约束）

- `POST .../knowledge/{id}/workflow/import` **会覆盖**该库当前入库工作流（与 UI「是否覆盖」一致）。  
- **禁止**把 MinerU 模板导入到用户**会话里已经建好、且仍要保留原编排**的知识库。  
- **正确做法**：`create_knowledge.py --kind workflow` **新建**一个空工作流知识库 → 再 `import_knowledge_workflow.py` 导入到**新库 id**。  
- 仅当用户**明确指定**某个已有 workflow 库 id，并确认「允许覆盖该库工作流」时，才可对旧 id 导入（脚本需 `--allow-overwrite`）。  
- 导入**不会**替代「删库重建」去抹掉用户其它库；但切勿误用已有库 id。

#### 执行步骤（脚本）

```text
1. 用户已确认使用 MinerU，并选定 online / local
2. download_kbwf_template.py --preset mineru-pdf-rag|mineru-local-md --out ./tpl.kbwf
   （从飞致云商店目录解析最新 downloadUrl，勿手写过期直链）
3. list_embedding_models → embedding_model_id
4. create_knowledge.py --kind workflow --name <新名称> --embedding-model-id EMBED --yes
   → 记下新 knowledge_id（不要复用旧库）
5. import_knowledge_workflow.py --knowledge-id <新id> --file ./tpl.kbwf --allow-overwrite --yes
6. 按模板 README 配置工具节点参数（在线 Token / maxkb_base_url，或本地 mineru_gradio_url 等）
   （工作流知识库**支持** tool-lib-node / tool-node / 数据源型工具，见 §2）
7. debug_knowledge_workflow.py --knowledge-id <新id> --file <样例.pdf或md> --yes
   → 轮询至 SUCCESS 再继续；失败则修编排/参数后重试（**发布前必调**）
8. publish_knowledge.py --knowledge-id <新id> --yes
9. 再挂到对话智能体检索；可用 hit_test 验收
```

若商店页打不开：脚本仍走 `https://apps.fit2cloud.com/app-store/v1/software` 拉清单；失败时告知用户手动从商店页下载 `.kbwf` 后只跑步骤 3～5。

### 1.3 库类型总决策树

```text
主文档是 PDF？ ──是──► 解释普通分段局限 → 请用户确认 MinerU？
        │                 │是 → §1.2 新建 workflow 库 + 导入模板
        │                 │否 → base + 普通分段（注明风险）
        │否
        ▼
DOCX / MD / TXT / FAQ / 表格？ ──是──► base（普通分段或专用接口）
        │否
        ▼
主要来源是公开网址？ ──是──► web
        │否
        ▼
需要自定义多步入库？ ──是──► workflow（自建或其它模板）
        │否
        ▼
仍优先 base
```

### 1.4 补充选型

| 场景 | 建议 |
|------|------|
| 问答对 / Excel 表格为主 | **base** + QA/表格接口，不为格式另建 workflow |
| 智能体只要检索、文档已在库 | **不新建库**，挂已有 `knowledge_id` |
| 多业务域隔离 | **多个库**按域拆，避免混杂 |
| DOCX + PDF 混合 | DOCX 进 base；PDF 进 **单独的** MinerU workflow 库（或用户同意后分文档策略），勿强行混一种差效果管线 |
| 仅临时试玩非 PDF | base + 少量 MD/TXT |

对用户说明时（小白）：「普通文档库 / 网页库 / 可编排入库的高级库」；PDF 可说「先解析再入库的专业方案（MinerU）」。
---

## 2. 工作流知识库制作规范（`--kind workflow`）

工作流知识库 = 知识库 + **入库工作流**（与「对话智能体工作流」不同）。节点类型见工作流 [nodes-reference.md](../maxkb-v2-workflow/nodes-reference.md)「知识库工作流专用」。

### 推荐拓扑（必须按此思路设计）

```text
数据源 →（可选：工具 / AI 清洗）→ 文档解析(extract) → 分段(split) → 写入并向量化(write)  〔终结〕
```

| 步骤 | 典型节点 type | 规范 |
|------|---------------|------|
| 1 数据源 | `data-source-local-node` / `data-source-web-node` / **数据源型** `tool-lib-node` | 本地与 Web 二选一或分支；工具作数据源时输出可接提取的 `file_list`/`result` |
| 2 可选加工 | `tool-lib-node` / `tool-node` / `tool-workflow-lib-node` / `ai-chat-node` 等 | **支持**调用自定义工具、MCP、AI（菜单允许的节点均可）；MinerU 模板即工具节点解析 PDF |
| 3 解析 | `document-extract-node` | 本地文件必须先提取；Web 已含 content 可跳过 |
| 4 分段 | `document-split-node` | 规则与下方「分段标准」一致 |
| 5 写入 | `knowledge-write-node` | **必须作为终结**；触发向量化 |

另有 `knowledge-base-node` 承载库基本信息（类似应用 base-node）。

**工具节点说明（易漏）**：知识库工作流菜单明确包含「自定义工具 / 工具库 / 工作流工具」，以及条件、循环、变量聚合等。Agent **不得**假设「工作流知识库不能调工具」。需要外部解析（MinerU）、HTTP、脚本清洗时，用 `tool-lib-node`（或内联 `tool-node`），遵守 [SANDBOX.md](../SANDBOX.md)。

### 入库数据契约（工具 / AI 输出形状 — 硬约束）

工具与 AI **不能**随便吐文本就接到写入。中间数据只有固定几档，详见 **[ingest-io-contracts.md](ingest-io-contracts.md)**（编排前必读）：

| 档 | 形状摘要 | 可接下游 |
|----|----------|----------|
| **A** `file_list` | `[{file_id, name}]` | 仅 → 文档内容提取 |
| **B** `document_list` | `[{name, content}]` | 仅 → 文档分段 |
| **C** `paragraph_list` | `[{name, paragraphs:[{content,…}]}]` | → **知识库写入**（唯一） |
| 字符串 | AI 的 `answer` / 纯文本 | **不能**直接写入；须经参数提取或工具组装成 B/C |

- 工具节点对外字段只有 **`result`**，`return` 值必须是 A/B/C 之一（视接线而定）。  
- AI 节点主输出是 **`answer`（string）**；提示词「输出」段必须贴 B 或 C 的 JSON schema，再用 `parameter-extraction-node` / 工具转成 list。  
- **禁止**：`answer` → 写入；B → 写入；A → 分段/写入。  

保存或导入后仍须 `debug_knowledge_workflow.py`；在 `details` 里核对各节点输出形状再发布。

### 自动调试（发布前必做）

编排保存或 `.kbwf` 导入并配参后，**发布前必须自动调试**，不要只口头说「请到界面点调试」：

```bash
# 本地数据源：上传样例文件并跑通入库图
python debug_knowledge_workflow.py --knowledge-id KID --file ./sample.md --yes \
  --host HOST --workspace WS --api-key KEY

# Web 数据源
python debug_knowledge_workflow.py --knowledge-id KID --source-url https://example.com/help --yes \
  --host HOST --workspace WS --api-key KEY
```

脚本会：`POST .../debug` → 轮询 `GET .../action/{id}` 至 `SUCCESS` / `FAILURE`。  
失败时根据 `details` 修节点参数或工具配置，再调一次；**仅 SUCCESS 后**再 `publish_knowledge.py`。

### 制作与发布检查清单

1. `create_knowledge.py --kind workflow ... --yes` 拿到知识库 id。  
2. 在库的工作流中按上表串好节点（可含工具）；**禁止**只有数据源没有 write。  
3. `debug_knowledge_workflow.py ... --yes` 用样例文件/URL **自动调试跑通**。  
4. `publish_knowledge.py --knowledge-id ID --yes` 后，对话侧智能体才能稳定检索该库。  
5. 变更分段、工具或源规则后：再 debug → 再 publish；必要时对文档 `batch_refresh` / 整库 `PUT .../embedding`。  
6. 与对话智能体分工：workflow 库管「如何入库」；对话应用管「如何检索与回答」——不要把 RAG 对话图塞进知识库工作流。

### 工作流知识库 CRUD（完整）

| 操作 | 脚本 | 门禁 |
|------|------|------|
| 创建 | `create_knowledge.py --kind workflow` | `--yes` |
| 查看 | `get_knowledge.py`（`--with-workflow` 看入库图） | 无 |
| 改元数据 | `update_knowledge.py`（name/desc/folder/embedding） | `--yes` |
| 改入库图 | `save_knowledge_workflow.py` 或 `import_knowledge_workflow.py` | `--yes`（导入另需 `--allow-overwrite`） |
| **调试** | **`debug_knowledge_workflow.py`** | `--yes`；发布前必跑 |
| 发布 | `publish_knowledge.py` | `--yes` |
| 导出 | `export_knowledge_workflow.py` | 无 |
| 删除 | `delete_knowledge.py` | 用户明确要求 → 回复「确认删除」→ `--confirm-name` 与现名一致 + `--yes` |

### 何时从 base「升级」到 workflow

- **PDF 需 MinerU**（§1.2）：新建 workflow 库并导入商店 `.kbwf`，不要改写用户已有库；  
- 要多源合并、按来源不同清洗规则；  
- 要在分段前做结构化抽取/过滤；  
- 运营希望入库流程可视化、可发布版本。  

否则保持 base + `ingest_file` / split + batch_create（DOCX 等）。

---

## 3. 分段标准（split / 入库）

适用于 **base** 的 `document/split` → `batch_create`，以及 **workflow** 内 `document-split-node` 的参数对齐。

### 3.1 核心参数

| 参数 | 含义 | 推荐默认 | 调整规则 |
|------|------|----------|----------|
| `limit` | 单段最大字符约数 | **512～1024**（问答/制度）；长文论述可 **1024～2048**；脚本默认 4096 偏大，生产建议按文档类型下调 | 段太长→检索噪声大；太短→答案碎片化 |
| `with_filter` / 自动清洗 | 去多余空白、噪声 | **开启**（`true`） | 代码/表格保留格式时可关 |
| `patterns` | 分段正则（可多条） | 先 `GET split_pattern` 选预设；无把握用换行/`\n\n` | 标题型文档按「第 x 章」等标题切；纯散文少用过碎 pattern |
| `problem_list` | 段关联问题 | FAQ 强烈建议填 | 提高问法命中；手册可后置「生成相关问题」 |

脚本：

- `split_document.py --limit ... --pattern ...`  
- `batch_create.py --normalize-split`（兼容 split 预览的 `content:[{title,content}]`）  
- `ingest_file.py`：split + batch_create 一条龙（仍要 `--yes`）

### 3.2 按文档类型的分段标准

| 文档类型 | limit 建议 | pattern / 切法 | 其他 |
|----------|-----------|----------------|------|
| **DOCX / 手册** | 512～1200 | 按章节标题、条款号 | **普通分段**；title=章节名；保持条款完整 |
| **FAQ / 问答** | 256～800 | 按「问/答」或空行；一段一问一答 | `title`=问题摘要；`problem_list` 备近义问法 |
| **长报告 / 论文（已是 MD/DOCX）** | 800～2048 | 按标题层级或 `\n\n` | 可略高 similarity 检索 |
| **PDF（未用 MinerU）** | 不推荐 | — | 先走 §1.2；若用户坚持普通分段，limit 宜偏小并加强 hit_test |
| **PDF→MinerU 后的 Markdown** | 512～1500 | 按 Markdown 标题 `#` / `##` | 在 workflow 的 split 节点配置；保留图表上下文 |
| **表格 / CSV** | 视行 | 优先走 **table** 文档接口 | 一行或一实体一段 |
| **代码 / 配置** | 512～1500 | 按函数/文件；`with_filter=false` | 少用语义清洗 |
| **网页（web 库）** | 同手册 | selector 先收窄正文 | 同步策略 `replace` vs `complete` 需业务确认 |

### 3.3 入库与质检规范

1. **先 preview 再落库**：`split_document.py --out preview.json`，人工或 Agent 抽查 3～5 段是否语义完整。  
2. **batch_create** 元素必须含 `name` + `paragraphs[{title,content,is_active,problem_list}]`。  
3. 落库后 **`hit_test`**：用 3～5 条真实用户问法；`search_mode` 建议先 `blend`，对比 `embedding` / `keywords`。  
4. `similarity`：通用 0.5～0.6；关键词短 query 可降到 0.3 观察（空结果≠接口失败）。  
5. `top_number`：命中测试 3～5；对话节点 `top_n` 常 3～5，与库内段长匹配。  
6. 大改分段规则后：对受影响文档刷新向量，或整库 `PUT .../embedding`。  
7. **安全**：分段内容勿写入密钥；用户文档遵守其数据合规要求。

### 3.4 智能体侧检索衔接（建库后）

对话工作流 `search-knowledge-node` 推荐与库分段一致：

- `search_mode`：`embedding` | `keywords` | `blend`（综合场景默认 **blend**）  
- `top_n`：3～5  
- `max_paragraph_char_number`：与段长匹配，常用 3000～5000  
- 多库：按域挂多个 id，或并行检索再汇聚（见 topology-samples）

---

## 4. 推荐操作顺序

```text
1. list_embedding_models → 选定 embedding_model_id
2. 按 §1 / §1.1 文档类型选型（PDF 先确认 MinerU）
3. create_knowledge --kind ... --yes
   （MinerU：必须新建 workflow 库，勿覆盖用户已有库）
4. base: ingest_file / split→batch_create（DOCX 等）
   web: 配 URL/selector，必要时 sync
   MinerU: download_kbwf_template → import_knowledge_workflow → 配参 → publish
   其它 workflow: 按 §2 自建编排 → debug → publish
5. hit_test 验收问句
6. 智能体 search-knowledge-node 挂本库 id
```

---

## 5. 脚本

| 脚本 | 用途 |
|------|------|
| `list_embedding_models.py` | 向量模型（走 `model_list`，兼容 API Key） |
| `list_knowledge.py` | 列表 |
| `get_knowledge.py` | 详情；`--with-workflow` 拉入库工作流 |
| `create_knowledge.py` | `--kind base\|web\|workflow` |
| `update_knowledge.py` | 改 name/desc/folder/embedding 等元数据 |
| `save_knowledge_workflow.py` | PUT 入库工作流图 `{work_flow}` |
| `publish_knowledge.py` | 发布入库工作流 |
| `download_kbwf_template.py` | 从飞致云商店拉取最新 `.kbwf`（MinerU 等） |
| `import_knowledge_workflow.py` | 将 `.kbwf` 导入指定工作流知识库（覆盖编排；需 `--allow-overwrite`） |
| `export_knowledge_workflow.py` | 导出 `.kbwf` |
| `debug_knowledge_workflow.py` | **工作流知识库自动调试**（上传样例 / Web URL → 轮询至结束；发布前必跑） |
| `split_document.py` / `batch_create.py` / `ingest_file.py` | 分段入库（支持 `content:[{title,content}]`） |
| `list_split_patterns.py` | 预设分段正则（若有） |
| `hit_test.py` | 命中测试（`embedding`/`keywords`/`blend`） |
| `delete_knowledge.py` | **删除（明确要求 +「确认删除」+ `--confirm-name` + `--yes`）** |

```bash
# DOCX / 普通文档 → base
python list_embedding_models.py --host HOST --workspace WS --api-key KEY
python create_knowledge.py --kind base --name faq --embedding-model-id EMBED --yes \
  --host HOST --workspace WS --api-key KEY
python ingest_file.py --knowledge-id KID --file ./a.docx --limit 1024 --yes \
  --host HOST --workspace WS --api-key KEY

# PDF → MinerU（用户确认后；始终新建 workflow 库再导入）
python download_kbwf_template.py --preset mineru-pdf-rag --out ./mineru.kbwf
python create_knowledge.py --kind workflow --name pdf-mineru --embedding-model-id EMBED --yes \
  --host HOST --workspace WS --api-key KEY
python import_knowledge_workflow.py --knowledge-id NEW_KID --file ./mineru.kbwf \
  --allow-overwrite --yes --host HOST --workspace WS --api-key KEY
python debug_knowledge_workflow.py --knowledge-id NEW_KID --file ./sample.pdf --yes \
  --host HOST --workspace WS --api-key KEY
python publish_knowledge.py --knowledge-id NEW_KID --yes \
  --host HOST --workspace WS --api-key KEY

# 查看 / 改元数据 / 导出
python get_knowledge.py --knowledge-id NEW_KID --with-workflow \
  --host HOST --workspace WS --api-key KEY
python update_knowledge.py --knowledge-id NEW_KID --desc "更新说明" --yes \
  --host HOST --workspace WS --api-key KEY
python export_knowledge_workflow.py --knowledge-id NEW_KID --out ./backup.kbwf \
  --host HOST --workspace WS --api-key KEY

# 删除（须用户回复「确认删除」后）
python delete_knowledge.py --knowledge-id NEW_KID --confirm-name "pdf-mineru" --yes \
  --host HOST --workspace WS --api-key KEY

python hit_test.py --knowledge-id KID --query "如何重置密码" --search-mode blend \
  --host HOST --workspace WS --api-key KEY
```
