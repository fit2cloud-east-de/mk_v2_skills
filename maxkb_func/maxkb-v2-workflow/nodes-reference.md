# Workflow Nodes Reference

`type` 字符串与 `ui/src/enums/application.ts` / `nodes/*/index.ts` 一致。业务参数在 `properties.node_data`。

## 固定基础节点

### base-node

```json
{
  "id": "base-node",
  "type": "base-node",
  "properties": {
    "stepName": "基本信息",
    "node_data": {
      "name": "应用名",
      "desc": "",
      "prologue": "开场白",
      "tts_type": "BROWSER",
      "file_upload_enable": false,
      "file_upload_setting": {
        "maxFiles": 3,
        "fileLimit": 50,
        "document": true,
        "image": false,
        "audio": false,
        "video": false,
        "other": false,
        "otherExtensions": ["ppt", "doc"]
      }
    },
    "user_input_field_list": [],
    "api_input_field_list": [],
    "chat_input_field_list": [],
    "user_input_config": { "title": "用户输入" }
  }
}
```

支持格式（开启对应开关后）：文档 TXT/MD/DOCX/HTML/CSV/XLSX/XLS/PDF；图 JPG/PNG/GIF；音 MP3/WAV…；视频 MP4…；其它自定义后缀。默认最多约 3～10 文件、单文件数十 MB（以 `file_upload_setting` 为准）。

### start-node

```json
{
  "id": "start-node",
  "type": "start-node",
  "properties": {
    "stepName": "开始",
    "config": {
      "fields": [{ "label": "用户问题", "value": "question" }],
      "globalFields": [
        { "label": "当前时间", "value": "time" },
        { "label": "历史聊天记录", "value": "history_context" },
        { "label": "对话 ID", "value": "chat_id" }
      ]
    }
  }
}
```

运行时上下文：`question`, `document`, `image`, `audio`, `video`, `other`, `memory`；全局还有 `chat_user_id`, `chat_user_type`, `chat_user`, `chat_user_group` 等。

---

## 应用工作流常用节点

| type | 关键 node_data | 主要输出 |
|------|----------------|---------|
| `ai-chat-node` | `model_id`, `system`, `prompt`, `dialogue_number`, `is_result`, `model_params_setting`, `tool_ids`, `mcp_*`, `vision` | `answer`, `reasoning_content`, `history_message` |
| `search-knowledge-node` | `knowledge_id_list`, `knowledge_setting`, `question_reference_address`, `search_scope_*` | `paragraph_list`, `data`, `directly_return`, `is_hit_handling_method_list` |
| `search-document-node` | 文档范围检索 | 文档列表相关 |
| `question-node` | 问题优化模型/提示词 | 优化后问题 |
| `condition-node` | `branch[]`（IF/ELSE IF/ELSE + conditions） | 走 `branch_id` 出口 |
| `intent-node` | 意图分类 | `category`, `reason`；多出口 |
| `reply-node` | `reply_type`: `content`\|`referencing`, `content`/`fields`, `is_result` | 回复文本 |
| `tool-node` | `code`, `input_field_list`, `is_result` | `result` |
| `tool-lib-node` | `tool_lib_id`, `input_field_list` | `result` |
| `tool-workflow-lib-node` | `tool_lib_id` + 输入映射 | 动态输出字段 |
| `mcp-node` | MCP server / tools | 工具调用结果 |
| `application-node` | 子应用 id | 子应用回答 |
| `reranker-node` | 重排模型与文档引用 | 重排后段落 |
| `form-node` | 表单字段 | 中断等人填；可续跑 |
| `document-extract-node` | 文档内容提取 | 文本 |
| `document-split-node` | 分段规则 | 分段列表 |
| `parameter-extraction-node` | 参数 schema | 提取字段 |
| `variable-assign-node` | 赋值列表 | 变量 |
| `variable-splitting-node` / `variable-aggregation-node` | 分割/聚合 | 变量 |
| `image-understand-node` / `video-understand-node` | 多模态理解 | 描述文本 |
| `image-generate-node` / `text-to-video-node` / `image-to-video-node` | 生成 | 媒体 |
| `speech-to-text-node` / `text-to-speech-node` | STT/TTS | `result` |
| `loop-node` (+ `loop-body-node`, `loop-start-node`, `loop-continue-node`, `loop-break-node`) | 循环 | 循环结果 |

### search-knowledge-node 默认检索

```json
{
  "knowledge_id_list": ["<uuid>"],
  "knowledge_setting": {
    "top_n": 3,
    "similarity": 0.6,
    "max_paragraph_char_number": 5000,
    "search_mode": "embedding"
  },
  "question_reference_address": ["start-node", "question"],
  "show_knowledge": false,
  "search_scope_type": "custom",
  "search_scope_source": "knowledge"
}
```

`search_mode`：`embedding` | `keywords` | `blend`。

### condition-node 分支

```json
{
  "branch": [
    {
      "id": "branch-uuid",
      "type": "IF",
      "condition": "and",
      "conditions": [
        { "field": ["start-node", "question"], "compare": "is_not_null", "value": "" }
      ]
    },
    { "id": "else-uuid", "type": "ELSE", "condition": "and", "conditions": [] }
  ]
}
```

出口边：`sourceAnchorId = "{nodeId}_{branchId}_right"`。

比较符含：`is_null`, `is_not_null`, `eq`, `not_eq`, `contain`, `not_contain`, `gt`, `ge`, `lt`, `le`, `regex` 等。

### tool-node（工作流内自定义代码）

```json
{
  "code": "def main(arg1):\n    return arg1",
  "input_field_list": [
    {
      "name": "arg1",
      "type": "string",
      "source": "reference",
      "value": ["start-node", "question"],
      "is_required": true
    }
  ],
  "is_result": false
}
```

`source`：`custom` | `reference`；`type`：`string|int|dict|array|float`。  
内嵌 `tool-node` 可用引用数组。**禁止**在 code 里 `subprocess`/`markitdown` 等（见 `SANDBOX.md`）。

### tool-lib-node（引用工具库）— 绑定陷阱

执行时工具定义里的 `source` 会覆盖节点上的 `source`。请用 **模板字符串**：

```json
{
  "tool_lib_id": "<uuid>",
  "input_field_list": [
    {
      "name": "text",
      "type": "string",
      "source": "custom",
      "value": "{{内嵌工具.result}}",
      "is_required": true
    }
  ],
  "is_result": false
}
```

不要用 `"value": ["node-id","result"]`，会报类型转换错误。

### AI 节点提示词规范（强制）

凡调用大模型的节点（含但不限于 `ai-chat-node`、`question-node`、`intent-node`、`parameter-extraction-node`、`image-understand-node`、`video-understand-node`，以及带自定义提示词的多模态/重排说明），**落地时必须写完整提示词**，禁止仅用「你是助手」+ 一句空泛指令。

完整提示词须同时覆盖以下四段（可拆到 `system` / `prompt`，但四段缺一不可）：

| 段 | 含义 | 最少要求 |
|----|------|----------|
| **Role（角色）** | 身份、服务对象、专业领域 | 明确「你是谁 / 为谁服务 / 擅长什么」 |
| **限制（Constraints）** | 边界与安全 | 写清可答/不可答、是否必须基于检索、拒答话术、禁止编造等 |
| **输出（Output）** | 结构与格式 | 写清字段/版式/语气/长度；若下游要解析，给出严格 JSON/标签约定 |
| **示例（Examples）** | 少样本 | 至少 **1 组**「输入 → 期望输出」正例；复杂任务建议再加 1 组反例或边界例 |

推荐结构（写入 `system` + `prompt`）：

```text
# system
【Role】你是……，面向……，负责……。
【限制】
- 只能基于……回答；检索为空时说明无法确认，禁止编造。
- 不回答……；遇敏感问题回复……。
【输出】
- 先给结论，再给依据；依据须标注来源段落。
- 若无法回答，输出固定句式：……

# prompt
【上下文】
检索结果：{{知识库检索.data}}
用户问题：{{开始.question}}

【输出要求】按 system 中的输出约定作答。

【示例】
输入：……
输出：……
```

自检清单（保存工作流前）：

- [ ] Role 非空泛「助手」
- [ ] 限制含拒答/防编造（RAG 场景必有）
- [ ] 输出格式可被下游或业务验收
- [ ] 至少 1 个示例与真实任务同构
- [ ] 变量引用（`{{节点.字段}}`）正确

拓扑少样本里的短提示词仅为**骨架示意**；真正 `save_workflow` / 发布前必须按本规范补全。

### ai-chat-node 要点

```json
{
  "model_id": "<uuid>",
  "system": "【Role】你是企业知识库问答助手，面向内部员工解答制度与流程。\n【限制】仅依据检索结果作答；无依据时明确说明「未找到依据」，禁止编造；不讨论与业务无关话题。\n【输出】先一句话结论，再列 1～3 条依据（引用检索片段关键词）；无法回答时只输出：未在知识库中找到相关说明。",
  "prompt": "【上下文】\n检索结果：{{知识库检索.data}}\n用户问题：{{开始.question}}\n\n【示例】\n输入：年假最长几天？\n输出：结论：……。依据：……\n\n请按 system 约定作答。",
  "dialogue_number": 1,
  "dialogue_type": "WORKFLOW",
  "is_result": true,
  "model_params_setting": {},
  "model_setting": {
    "reasoning_content_enable": false,
    "reasoning_content_start": "<think>",
    "reasoning_content_end": "</think>"
  }
}
```

---

## 知识库工作流专用

| type | 作用 |
|------|------|
| `knowledge-base-node` | 知识库基本信息（类似 base） |
| `data-source-local-node` | 本地文件数据源 → `file_list` |
| `data-source-web-node` | Web 数据源 → `document_list` |
| `document-extract-node` / `document-split-node` | 解析 / 分段 |
| `knowledge-write-node` | 写入并向量化（终结） |

推荐链路：数据源 → 解析 → 分段 → 写入。

## 工具工作流专用

| type | 作用 |
|------|------|
| `tool-base-node` | 输入/输出参数定义 |
| `tool-start-node` | 执行起点 |

---

## 边与并行速查

```text
普通：source = "{id}_right" , target = "{id}_left"
分支：source = "{id}_{branchId}_right"
多下游：并行（ThreadPoolExecutor, max_workers=200）
汇合：properties.condition = AND | OR
禁用：properties.disabled = true → 跳过
异常分支：enableException + branch_id=exception
```
