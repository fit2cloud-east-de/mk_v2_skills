# 工作流知识库：入库数据契约（工具 / AI 必读）

> Agent 在编排或编写工具/`AI` 节点时**必须**遵守本文件。  
> 形状对不上 → 调试/生产直接失败（序列化校验或空写入）。

入库主链路的中间数据**种类很少、形状相对固定**。工具与 AI **不能**随意输出自由文本就接到「知识库写入」。

---

## 1. 四档标准形状（唯一合法货币）

按下游节点吃什么，只认下面四档。引用字段名以节点 `config.fields` 为准。

### A. `file_list` — 未解析文件（喂「文档内容提取」）

```json
[
  { "file_id": "019f…", "name": "手册.pdf" }
]
```

| 谁产出 | 输出字段 |
|--------|----------|
| `data-source-local-node` | `file_list` |
| 数据源型工具（实现了 `get_download_file_list` + `download`） | `result`（元素同左） |

**禁止**：把 `file_list` 直接接到分段或写入。

---

### B. `document_list` — 已有正文（喂「文档分段」）

```json
[
  {
    "id": "可选-常为file_id",
    "name": "文档显示名",
    "content": "全文纯文本或 Markdown"
  }
]
```

| 谁产出 | 输出字段 |
|--------|----------|
| `document-extract-node` | `document_list`（另有拼接字符串 `content`） |
| `data-source-web-node` | `document_list`（已含 content） |
| 自定义工具 / 参数提取（跳过提取时） | 须落成 **同结构的 list**，再接到分段的 `document_list` |

**禁止**：把 B 直接接到「知识库写入」（缺少 `paragraphs`）。

---

### C. `paragraph_list` — 已分段（喂「知识库写入」）

写入节点校验（`KnowledgeWriteParamSerializer`）要求 **文档数组**，每项至少有 `name`；真正有用的内容在 `paragraphs`：

```json
[
  {
    "name": "文档名（必填，1～128字）",
    "source_file_id": "可选-UUID",
    "meta": { "可选": "任意" },
    "tags": [{ "key": "k", "value": "v" }],
    "paragraphs": [
      {
        "content": "段正文（写入时实质必填；最长约 102400）",
        "title": "可选标题",
        "problem_list": ["可选关联问题"],
        "is_active": true,
        "chunks": ["可选子块；缺省则按 content 切"]
      }
    ]
  }
]
```

| 谁产出 | 输出字段 |
|--------|----------|
| `document-split-node` | `paragraph_list` |
| `variable-aggregation-node` | 自定义名（如模板 `Segmented_List`），**值必须仍是 C 形** |
| 工具 / 参数提取（跳过分段时） | 返回值必须是 **C 形 list**，写入节点引用该字段 |

**这是「知识库写入」唯一可直接吃的形状。**

---

### D. 写入预览 `write_content`（只读，勿再往下接）

```json
[{ "name": "…", "paragraphs": [{ "title": "…", "content": "…" }] }]
```

`knowledge-write-node` 的 `config.fields` 为空，UI 级联通常选不到；仅调试详情可见。

---

## 2. 工具节点（`tool-node` / `tool-lib-node`）输出约定

工具执行结果一律落在字段 **`result`**（类型 = 你 `return` 的 Python 对象）。

### 2.1 按接入点选返回值

| 下游接什么 | 工具 `return` 必须是 | 写入节点/分段引用 |
|------------|----------------------|-------------------|
| → 文档内容提取 | **A 形** list：`[{file_id, name}, …]` | 提取的 `document_list` 参数指到 `[工具节点, "result"]` |
| → 文档分段 | **B 形** list：`[{name, content}, …]` | 分段的 `document_list` → `result` |
| → 知识库写入 | **C 形** list：`[{name, paragraphs:[…]}, …]` | 写入的「输入内容」→ `result` |
| → 仅给 AI 看 | `str` / 任意 JSON | 仅作提示词变量，**不能**当写入输入 |

### 2.2 数据源型工具（`kind=data-source`）

若实现了 `get_download_file_list` + `download`：平台会下载并上传 File，**强制**把 `result` 变成 A 形 `[{file_id, name}]`。  
未实现下载钩子：`result` = 你的 `return`，形状仍须与下游契约一致。

### 2.3 常见错误

| 错误 | 后果 |
|------|------|
| `return "一段 Markdown 字符串"` 接到写入 | 校验失败 / 无法按文档落库 |
| `return {"content": "..."}` 单对象接到分段 | 分段期望 **list** |
| `return` 提取结果 B 形却接到写入 | 缺 `paragraphs`，写入空或失败 |
| 把工具输出字段配成 `answer` / `content` | 工具只有 `result` |

编写工具时：在代码注释与 `output` 说明里写明「本工具产出 A/B/C 哪一档」。调试用 `debug_knowledge_workflow.py` 看 `details` 里该节点的 `result`。

---

## 3. AI 节点（`ai-chat-node` 等）输出约定

AI 对话节点对外主字段是 **`answer`（字符串）**，另有 `reasoning_content` / `history_message`。  
**`answer` 不是 C 形，不能直接接到知识库写入。**

### 3.1 推荐接法

```text
… → AI（改写/清洗文本）→ 参数提取 parameter-extraction-node（抽成 B 或 C）
                      ↘ 或 → 工具（把 answer 组装成 A/B/C）
```

| 目标下游 | AI 提示词应要求 | 再经 |
|----------|-----------------|------|
| 分段 | 输出 **JSON 数组**，元素含 `name`+`content`（B） | `parameter-extraction-node` 抽成 list，或工具 `json.loads` |
| 写入 | 输出 **JSON 数组**，元素含 `name`+`paragraphs[{content,…}]`（C） | 同上 |
| 仅润色某一段文本 | 纯文本即可 | 下游工具负责包进 B/C |

### 3.2 AI 提示词「输出」段（强制写清）

每个用于入库的 AI 节点，提示词 **输出格式** 必须贴契约，例如（接到写入前）：

```text
只输出 JSON 数组，不要 Markdown 围栏，不要解释。schema：
[
  {
    "name": "string",
    "paragraphs": [
      { "title": "string", "content": "string", "problem_list": [], "is_active": true }
    ]
  }
]
```

接到分段前则改为 B 的 schema（`name`+`content`，无 `paragraphs`）。

### 3.3 禁止

- `ai-chat-node.answer` → `knowledge-write-node` 的输入  
- 提示词不写 schema，却指望模型「随便说说」能入库  
- 用 `reply-node` 的自由文案冒充分段结果  

---

## 4. 接线速查

```text
合法：
  本地文件.file_list     → 提取 → 分段.paragraph_list → 写入
  Web.document_list      → 分段 → 写入
  工具.result(A)         → 提取 → 分段 → 写入
  工具.result(B)         → 分段 → 写入
  工具.result(C)         → 写入
  AI.answer → 参数提取(C) → 写入
  AI.answer → 工具(组装C) → 写入

非法：
  file_list → 写入 / 分段
  document_list(B) → 写入
  answer(string) → 写入
  任意 dict 单对象 → 分段/写入（缺外层 list）
```

多路分段：用 `variable-aggregation-node`，各组引用的必须是 **C 形**；聚合输出名可自定义，但值仍是 C。

---

## 5. Agent 自检清单（保存 / 调试前）

1. 画出每条边：上游输出字段名 + **A/B/C/字符串** 哪一档。  
2. 写入节点的输入引用，确认是 **C**。  
3. 每个工具的 `return` 类型与档位写进节点说明；每个入库 AI 的「输出」段含 JSON schema。  
4. `debug_knowledge_workflow.py` 跑通；在 `details` 中核对关键节点字段形状，再 `publish`。  

---

## 6. 源码锚点

| 契约 | 位置 |
|------|------|
| 写入校验 | `apps/application/flow/step_node/knowledge_write_node/impl/base_knowledge_write_node.py` → `KnowledgeWriteParamSerializer` |
| 分段产出 | `…/document_split_node/impl/base_document_split_node.py` → `paragraph_list` |
| 提取产出 | `…/document_extract_node/impl/base_document_extract_node.py` → `document_list` |
| 工具 `result` / 下载型 A | `…/tool_lib_node/impl/base_tool_lib_node.py` |
| AI `answer` | `ui/src/workflow/common/data.ts` → `aiChatNode.config.fields` |
