# 工作流界面约束（编排硬规则）

生成 / 改写 `work_flow` 时按本节执行：**界面上灰掉、删不掉、系统固定的，一律保持原样；可变的只动业务配置。**

---

## 1. 固定节点（不可删、id/type 固定）

| 场景 | 固定节点 | 规则 |
|------|----------|------|
| **应用工作流** | `id=base-node`（基本信息）、`id=start-node`（开始） | 禁止删除、禁止改 id；`type` 与 id 一致 |
| **工作流知识库** | `id=knowledge-base-node`（基本信息） | id 不可改；详见知识库 skill |
| **工具工作流** | `tool-base-node`、`tool-start-node` | 不可删 |
| **循环体内** | `loop-start-node`（及循环体结构节点） | 不可当普通节点删掉 |

界面删除固定节点会直接报错拦截。自由节点（AI、检索、条件、工具等）可删可改。

---

## 2. 界面只读 / 系统固定（禁止 AI 改）

| 位置 | 固定内容 | 可变部分 |
|------|----------|----------|
| **意图识别** `intent-node` | 末条 `isOther: true`，`content` 必须是 **`其他`**；不可删该条 | 仅增删/改写 `isOther: false` 的意图文案；`model_id`、输入引用、历史轮次 |
| **条件分支** `condition-node` | 末条 `type: "ELSE"`，`conditions: []`；IF/ELSE IF/ELSE **标签由结构决定**，不是可改文案 | IF / ELSE IF 的条件字段、比较符、值；分支条数（至少 IF+ELSE） |
| **分支锚点表** | `properties.branch_condition_list` 必须与 `branch[].id` 同步（缺则无「+」、线乱跑） | 保存脚本可自动补；`height` 行高意图常用 12 |
| **开始节点内置字段** | `question`；全局内置 `time` / `history_context` / `chat_id` / `chat_user_*` 等 | 用户输入/接口传参/会话变量声明后映射到 global/chat；上传开关打开后的 document/image… |
| **异常信息** | `exception_message` 仅运行时产出 | 只可在下游模板引用，勿在 `node_data` 预填 |
| **节点宽高** | 意图/条件须按分支数写合理 `height`；其它节点可省略由画布测量 | 勿抄超大导出值；勿漏 `branch_condition_list` |
| **分支锚点高度** | `branch_condition_list[].height` 为**行**高（常见 12） | 勿当成整节点 height |

### 意图「其他」（高频踩坑）

```json
{ "id": "<稳定uuid>", "content": "其他", "isOther": true }
```

- 必须有且仅有一条，放在 `branch` **末尾**  
- **禁止**改成「别的 / unknown / default / 其它意图」等  
- **禁止**去掉 `isOther` 或把普通意图标成 other  
- 改错后界面输入框仍为禁用，用户无法在前台改回  

保存脚本默认会把 `isOther` 文案纠正为「其他」。

---

## 3. 必选项与推荐默认值

| 配置 | 要求 |
|------|------|
| 应用图 | 始终含 `base-node` + `start-node` |
| AI / 意图 / 问题优化等 | `model_id`（或合法模型引用）必填 |
| 意图 | ≥1 条普通意图 + 1 条「其他」；`content_list` 指向问题来源 |
| 条件 | ≥1 个 IF + 1 个 ELSE；`is_null` 类比较仍要带非空 `value`（常用 `1`） |
| 知识库检索 | `knowledge_id_list`、`question_reference_address`、`knowledge_setting`（`top_n`/`similarity`/`search_mode`） |
| 指定回复 | `reply_type` + `content` 或引用字段 |
| 工具库节点 | `tool_lib_id`；入参用**字符串模板** `{{节点名.字段}}` |
| 循环 | `loop_body` 非空（含 loop-start）；`loop_type` 为 ARRAY/NUMBER/LOOP |
| 视觉 AI | `vision: true` 时 `image_list` 必填；基本信息须开对应上传 |
| AI 提示词 | `system`/`prompt` 须含 Role / 限制 / 输出 / 示例 |

---

## 4. 谁可以当「结束」/ 对用户出话

**叶节点**＝有入边、无出边。叶节点若要对用户说话，应带 **`is_result: true`**（或界面「返回内容」打开）。

| 适合作为对话叶节点 | 不适合单独作为对话叶节点（须再接下文） |
|--------------------|----------------------------------------|
| `ai-chat-node`、`reply-node` | `condition-node`、`intent-node`（只分流） |
| `tool-node` / `tool-lib-node`（开返回） | `search-knowledge-node`（只召回，需 AI/回复消费） |
| 表单 `form-node`（等人填，可中断） | `document-extract/split`、变量聚合/赋值（中间处理） |
| 多模态生成/理解（按场景） | `start-node` / `base-node`（固定起点/配置，不是业务终点） |

工作流知识库：**每条数据源分支终点必须是** `knowledge-write-node`，其它节点不能当入库结束。

异常分支：开了 `enableException` 必须拉 `{id}_exception_right` → 兜底（回复/AI/工单等），见 [exception-handling.md](exception-handling.md)。

---

## 5. 模块必有结构（按图类型）

### 应用工作流

```text
base-node + start-node
  → 自由编排（检索 / 条件 / 意图 / AI / 工具 / …）
  → 叶节点建议 is_result=true（对用户有输出）
```

### 工作流知识库

```text
knowledge-base-node（固定 id）
  + ≥1 个 kind=data-source（本地 / Web / 数据源工具）
  → … → knowledge-write-node（每条分支终点）
```

### 工具工作流

```text
tool-base-node + tool-start-node → 执行链
```

---

## 6. 边与锚点（固定写法）

| 边类型 | sourceAnchorId |
|--------|-----------------|
| 普通 | `{nodeId}_right` |
| 条件 / 意图分支 | `{nodeId}_{branchId}_right`（**禁止**意图/条件用无 branchId 的 `{nodeId}_right`） |
| 异常 | `{nodeId}_exception_right`（须先 `enableException: true`） |
| 目标 | `{targetId}_left` |

意图/条件还须有 `properties.branch_condition_list`（与 `branch[].id` 对齐），否则分类旁无「+」、已有边找不到锚点会飞线。

汇合：下游 `properties.condition` 为 `AND`（全到齐）或 `OR`（任一即可）。

---

## 7. 可自由改 vs 勿乱动（速查）

| 可改 | 勿乱动 |
|------|--------|
| 自由节点的 `stepName`（保持唯一、提示词用中文名） | 固定节点 id/`type` |
| `node_data` 业务字段（模型、提示词、知识库 id、工具入参…） | 意图「其他」、条件 `ELSE` 结构标签 |
| 自由节点之间的边 | 删掉唯一数据源 / 唯一写入（知识库图） |
| `is_result`、异常开关与兜底边 | 臆造 `exception_message`；乱写超大 height/width |
| 用户输入 / 接口 / 会话变量声明 | 与内置 global 字段抢同名冲突 |

---

## 8. 落地自检清单

- [ ] 固定节点还在、id 未改  
- [ ] 意图末条为 `其他` + `isOther: true`；条件末条为 `ELSE` + 空 conditions  
- [ ] 意图/条件已写 `branch_condition_list`（id 与 branch 一致），出口边带 `branchId`  
- [ ] 叶节点对用户有输出时 `is_result: true`；条件/意图/检索后还有 AI 或回复  
- [ ] 知识库图：有数据源、分支到写入  
- [ ] 意图/条件有合理 height；其它节点未乱写超大 height/width  
- [ ] AI 提示词四段齐全；引用用 `{{步骤名.字段}}`  

相关：[nodes-reference.md](nodes-reference.md) · [inputs-and-variables.md](inputs-and-variables.md) · [exception-handling.md](exception-handling.md)
