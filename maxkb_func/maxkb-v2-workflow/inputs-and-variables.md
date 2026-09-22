# 工作流：用户输入 / 接口传参 / 会话变量 / 文件上传

对照 MaxKB **2.10.3-lts**。配置都在 **基本信息**（`base-node`）；运行时进入 **开始** 节点的全局 / 会话 / 文件字段。

---

## 1. 四类对照

| 界面（基本信息） | JSON 位置 | 运行时进哪 | 模板引用 | 谁填值 |
|------------------|-----------|------------|----------|--------|
| 用户输入 | `properties.user_input_field_list` | **全局** `workflow.context` | `{{global.字段名}}` | 对话前表单 / 调试 `form_data` |
| 接口传参 | `properties.api_input_field_list` | **全局**（同上） | `{{global.变量名}}` | API / OpenAI 兼容里的 `form_data` |
| 会话变量 | `properties.chat_input_field_list` | **会话** `chat_context`（跨轮可持久） | `{{chat.字段名}}` | 工作流内「变量赋值」等写入，不是每轮表单 |
| 文件上传 | `node_data.file_upload_enable` + `file_upload_setting` | **开始节点** `document/image/audio/video/other` | `{{开始.image}}` 等 | 聊天上传或 `chat_message` 的 `*_list` |

内置全局（无需自建）：`time`、`history_context`、`chat_id`、`chat_user_id`、`chat_user_type`、`chat_user`、`chat_user_group`。  
开启长期记忆后开始节点多 `memory` → `{{开始.memory}}`（≠ 会话变量、≠ history_context）。

**不要混用：**

- `{{global.x}}` ≠ `{{chat.x}}` ≠ `{{开始.question}}`
- 用户输入 / 接口传参字段名**不能重复**（UI 会拦）；二者都进 global，同名时运行时以 `form_data` 合并覆盖默认值
- 会话变量要先在基本信息声明，再用变量赋值节点写 `["chat","字段"]`

---

## 2. 用户输入（`user_input_field_list`）

聊天窗在开聊前弹出的表单项；值进入全局。

```json
"user_input_field_list": [
  {
    "field": "role",
    "label": "角色",
    "type": "input",
    "default_value": "工程师",
    "required": false
  }
],
"user_input_config": { "title": "用户输入" }
```

说明：

- 变量名用 `field`（历史数据也可能是 `variable`）；开始节点 `globalFields` 的 `value` 取 `field || variable`
- `type` 常见：`input`、下拉/多选等（以动力学表单为准）
- 脚本落地后，开始节点 `config.globalFields` 应含该字段（与内置 time 等并列）；界面会 `refreshFieldList` 自动刷，纯 JSON 保存时请一并写上

引用：

```text
{{global.role}}
引用数组：["global", "role"]
```

调试 / 生产传值（`chat_message` 或 completions）：

```json
"form_data": { "role": "产品经理" }
```

---

## 3. 接口传参（`api_input_field_list`）

给 **API / 应用 Key 调用** 用的全局入参；聊天窗不一定展示，但同样进 `form_data` → global。

```json
"api_input_field_list": [
  {
    "variable": "tenant_id",
    "name": "租户ID",
    "type": "input",
    "is_required": true,
    "default_value": ""
  }
]
```

说明：

- 变量名键是 **`variable`**（不是 `field`）；展示名多为 `name`
- 与用户输入字段名冲突时 UI 禁止保存
- 合并顺序（开始节点）：默认值（user）→ 默认值（api）→ 请求里的 `form_data`（后写覆盖）

引用：`{{global.tenant_id}}` / `["global","tenant_id"]`。

---

## 4. 会话变量（`chat_input_field_list`）

跨本会话多轮保留的键；**不是**每轮用户再填一遍。声明在基本信息，读写走 `chat` 命名空间。

```json
"chat_input_field_list": [
  { "field": "last_order_id", "label": "最近订单号" }
]
```

开始节点会出现 `config.chatFields`；模板：

```text
{{chat.last_order_id}}
引用数组：["chat", "last_order_id"]
```

写入：用 **变量赋值** `variable-assign-node`，目标选会话字段（`fields: ["chat","last_order_id"]`）。运行时写入 `chat_context` 并 `set_chat_variable` 持久化。

与长期记忆区别：会话变量是你声明的键值；`memory` 是平台长期记忆能力抽出的文本。

---

## 5. 文件上传

### 5.1 基本信息开关

```json
"node_data": {
  "file_upload_enable": true,
  "file_upload_setting": {
    "maxFiles": 3,
    "fileLimit": 50,
    "document": true,
    "image": false,
    "audio": false,
    "video": false,
    "other": false,
    "otherExtensions": ["PPT", "DOC"],
    "local_upload": true,
    "url_upload": false
  }
}
```

| 开关 | 开始节点字段 | 模板 | chat_message 对应 |
|------|--------------|------|-------------------|
| `document` | `document` | `{{开始.document}}` | `document_list` |
| `image` | `image` | `{{开始.image}}` | `image_list` |
| `audio` | `audio` | `{{开始.audio}}` | `audio_list` |
| `video` | `video` | `{{开始.video}}` | `video_list` |
| `other` | `other` | `{{开始.other}}` | `other_list` |

格式（开启后）：文档 TXT/MD/DOCX/HTML/CSV/XLSX/XLS/PDF；图 JPG/JPEG/PNG/GIF；音 MP3/WAV/OGG/ACC/M4A；视频 MP4/AVI/MKV/MOV/FLV/WMV；其它看 `otherExtensions`。`fileLimit` 单位 MB。

脚本保存时请同步开始节点 `config.fields`（在 `question` 后追加已开启的类型），否则引用面板可能缺字段。

### 5.2 与 AI 视觉

`ai-chat-node` 开 `vision: true` 后，`image_list` / `video_list` 常引用 `["start-node","image"]` / `["start-node","video"]`，故基本信息须先打开对应上传类型。详见 [nodes-reference.md](nodes-reference.md)「ai-chat-node：视觉开关」。

### 5.3 上传与对话

1. （可选）`POST .../oss/file` 拿到文件 id  
2. `chat_message` / completions 带上对应 `*_list`（元素为平台文件对象/id，与前端约定一致）  
3. 开始节点把列表放进 `document`/`image`/… 供下游引用  

---

## 6. 调试 body 最小示例

```json
{
  "message": "帮我看这张图",
  "stream": false,
  "form_data": {
    "role": "工程师",
    "tenant_id": "t-001"
  },
  "image_list": [],
  "document_list": [],
  "audio_list": [],
  "video_list": [],
  "other_list": []
}
```

`form_data` 的 key = 用户输入的 `field` 或接口传参的 `variable`。

---

## 7. 编排清单

- [ ] 用户可见表单项 → `user_input_field_list`，引用 `{{global.*}}`，调试带 `form_data`
- [ ] 仅 API 注入 → `api_input_field_list`，同样 `form_data`，勿与用户字段重名
- [ ] 跨轮状态 → `chat_input_field_list` + 变量赋值写 `chat.*`
- [ ] 要传文件 → `file_upload_enable` + 类型开关；下游用 `{{开始.document|image|...}}`
- [ ] 看图/视频对话 → 上传开 image/video + AI 节点 `vision`

内置 `question` / `time` / `history_context` 等勿当用户字段删改；自定义只动 `user_input` / `api_input` / `chat_input` 声明。详见 [ui-constraints.md](ui-constraints.md)。
