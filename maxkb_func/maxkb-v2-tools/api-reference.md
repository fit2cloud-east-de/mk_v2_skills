# Tools API Reference

Header：`Authorization: Bearer YOUR_SYSTEM_API_KEY`。前缀：`{ADMIN_API}/workspace/{WS}/tool`。

## CRUD

| Method | Path | Body |
|--------|------|------|
| GET | `` | 列表；Query: `folder_id` |
| GET | `/tool_list` | 全量可选列表 |
| GET | `/{page}/{size}` | 分页；Query: `folder_id`,`name`,`tool_type`,`scope` |
| POST | `` | Create，见下 |
| GET | `/{id}` | 详情 |
| PUT | `/{id}` | Edit |
| DELETE | `/{id}` | 删除 |
| PUT | `/{id}/edit_icon` | 图标 |
| GET | `/{id}/export` | 导出 `.tool` |
| POST | `/import` | 导入 |

### Create body

```json
{
  "name": "string",
  "desc": "string",
  "code": "string",
  "input_field_list": [],
  "init_field_list": [],
  "folder_id": "string",
  "is_active": true,
  "tool_type": "CUSTOM",
  "work_flow": null
}
```

`tool_type`：`CUSTOM` | `INTERNAL` | `MCP` | `SKILL` | `WORKFLOW`。

### Edit 额外字段

`init_params`（dict），以及 Create 中可选字段。

## Debug / Lint / Connection

| Method | Path | Body |
|--------|------|------|
| POST | `/debug` | `{ code, input_field_list, init_field_list, init_params, debug_field_list:[{name,value}] }` |
| POST | `/pylint` | `{ code }` |
| POST | `/test_connection` | MCP：`{ code }` |

## Workflow tool

| Method | Path |
|--------|------|
| PUT | `/{id}/workflow` |
| PUT | `/{id}/publish` |
| POST | `/{id}/debug` |

## Store / Internal / Skill

| Method | Path |
|--------|------|
| POST | `/{id}/add_internal_tool` |
| POST | `/{id}/add_store_tool` |
| POST | `/{id}/update_store_tool` |
| PUT | `/upload_skill_file` |
| GET | `/{id}/download_skill_file`（若部署提供） |

## Tool records（X-Pack 等）

```http
GET .../tool/{id}/tool_record/{page}/{size}
GET .../tool/{id}/tool_record/{record_id}
```

## curl：创建并调试

```bash
# 创建
curl -X POST "{ADMIN_API}/workspace/default/tool" \
  -H "Authorization: Bearer YOUR_SYSTEM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "echo",
    "desc": "echo input",
    "folder_id": "default",
    "code": "def main(text):\n    return text\n",
    "input_field_list": [
      {"name":"text","type":"string","source":"custom","is_required":true}
    ],
    "init_field_list": [],
    "is_active": true
  }'

# 调试（可不先创建）
curl -X POST "{ADMIN_API}/workspace/default/tool/debug" \
  -H "Authorization: Bearer YOUR_SYSTEM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def main(text):\n    return text\n",
    "input_field_list": [
      {"name":"text","type":"string","source":"custom","is_required":true}
    ],
    "init_field_list": [],
    "init_params": {},
    "debug_field_list": [{"name":"text","value":"hello"}]
  }'
```
