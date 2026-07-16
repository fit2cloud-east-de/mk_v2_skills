# Workflow API Reference

路径均相对 `{ADMIN_API}`，除非标明 Chat。Header：`Authorization: Bearer YOUR_API_KEY`。

## Application CRUD

| Method | Path | 说明 |
|--------|------|------|
| POST | `/workspace/{WS}/application` | 创建 |
| GET | `/workspace/{WS}/application` | 列表 |
| GET | `/workspace/{WS}/application/{page}/{size}` | 分页 |
| GET | `/workspace/{WS}/application/{id}` | 详情（含 `work_flow`） |
| PUT | `/workspace/{WS}/application/{id}` | 更新（可带 `work_flow`） |
| DELETE | `/workspace/{WS}/application/{id}` | 删除 |
| PUT | `/workspace/{WS}/application/{id}/publish` | 发布 |
| PUT | `/workspace/{WS}/application/{id}/move/{folder_id}` | 移动 |
| GET | `/workspace/{WS}/application/{id}/export` | 导出 `.mk` |
| POST | `/workspace/{WS}/application/folder/{folder_id}/import` | 导入 |

### PUT 常用可写字段

`name`, `desc`, `prologue`, `work_flow`, `model_id`, `knowledge_setting`, `model_setting`, `file_upload_enable`, `file_upload_setting`, `stt_*`, `tts_*`, `mcp_*`, `tool_*`, `long_term_*` 等。

## Debug / Chat

| Method | Path | Auth | 说明 |
|--------|------|------|------|
| GET | `/workspace/{WS}/application/{id}/open` | 系统 Key | 开 debug 会话 → `chat_id` |
| POST | `/chat_message/{chat_id}` | 系统 Key | 调试对话（admin 前缀下） |
| POST | `{CHAT_API}/{APP_ID}/chat/completions` | 应用 Key | OpenAI 兼容 |
| GET | `{CHAT_API}/open` | 应用 Key | 开生产会话 |
| POST | `{CHAT_API}/chat_message/{chat_id}` | 应用 Key | 生产对话 |
| GET | `{CHAT_API}/application/profile` | 应用 Key | 应用资料 |

### chat_message Body

```json
{
  "message": "string",
  "stream": true,
  "re_chat": false,
  "chat_record_id": null,
  "node_id": null,
  "runtime_node_id": null,
  "node_data": {},
  "form_data": {},
  "image_list": [],
  "document_list": [],
  "audio_list": [],
  "video_list": [],
  "other_list": [],
  "child_node": {}
}
```

### OpenAI completions Body

```json
{
  "messages": [{ "role": "user", "content": "..." }],
  "chat_id": null,
  "re_chat": false,
  "stream": false,
  "form_data": {},
  "image_list": [],
  "document_list": [],
  "audio_list": [],
  "other_list": []
}
```

`messages` 取最后一条 user 的 `content` 作为问题。

## Application Key

| Method | Path |
|--------|------|
| POST | `/workspace/{WS}/application/{id}/application_key` |
| GET | `/workspace/{WS}/application/{id}/application_key/{page}/{size}` |
| PUT | `/workspace/{WS}/application/{id}/application_key/{key_id}` |
| DELETE | `/workspace/{WS}/application/{id}/application_key/{key_id}` |

PUT body：`is_active`, `allow_cross_domain`, `cross_domain_list`, `is_permanent`, `expire_time`。

## Version

| Method | Path |
|--------|------|
| GET | `/workspace/{WS}/application/{id}/application_version` |
| GET | `/workspace/{WS}/application/{id}/application_version/{page}/{size}` |
| GET | `/workspace/{WS}/application/{id}/application_version/{version_id}` |
| PUT | `/workspace/{WS}/application/{id}/application_version/{version_id}` |

## work_flow 结构

```json
{
  "nodes": [
    {
      "id": "uuid-or-fixed",
      "type": "ai-chat-node",
      "x": 700,
      "y": 3400,
      "properties": {
        "stepName": "显示名（工作流内唯一）",
        "showNode": true,
        "condition": "AND",
        "config": { "fields": [{ "label": "...", "value": "answer" }] },
        "node_data": {}
      }
    }
  ],
  "edges": [
    {
      "id": "uuid",
      "type": "app-edge",
      "sourceNodeId": "start-node",
      "targetNodeId": "next-id",
      "sourceAnchorId": "start-node_right",
      "targetAnchorId": "next-id_left",
      "startPoint": { "x": 0, "y": 0 },
      "endPoint": { "x": 0, "y": 0 },
      "pointsList": [],
      "properties": {}
    }
  ]
}
```

固定 ID：`base-node`、`start-node`。其它节点用 UUID。

## 变量引用

- 节点输出：`{{节点显示名.字段}}` 或地址数组 `["node-id","field"]`
- 全局：`{{global.time}}` 等（`node_id === "global"`）
- 会话：`{{chat.xxx}}`（base-node 的 `chat_input_field_list`）

## 文件 OSS

```http
POST {ADMIN_API}/oss/file
Content-Type: multipart/form-data

file: <binary>
source_id: <app_or_knowledge_id>
source_type: APPLICATION | KNOWLEDGE | TOOL | DOCUMENT | CHAT | TEMPORARY_*
```
