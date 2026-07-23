# Knowledge API Reference

Header：`Authorization: Bearer YOUR_SYSTEM_API_KEY`。前缀：`{ADMIN_API}/workspace/{WS}/knowledge`。

## Knowledge Base

| Method | Path | Body / Query |
|--------|------|----------------|
| GET | `` | 列表；Query: `folder_id`,`name`,`desc` |
| GET | `/{page}/{size}` | 分页 |
| POST | `/base` | `{ name, folder_id, embedding_model_id, desc? }` |
| POST | `/web` | 上 + `source_url`, `selector?` |
| POST | `/workflow` | `{ name, folder_id, embedding_model_id, desc? }` |
| GET | `/{id}` | 详情 |
| PUT | `/{id}` | `name`,`desc`,`meta`,`application_id_list`,`file_size_limit`,`file_count_limit`,`embedding_model_id`,`folder_id`… |
| DELETE | `/{id}` | 删除 |
| PUT | `/{id}/embedding` | 整库重向量化 |
| POST | `/{id}/hit_test` | `{ query_text, top_number, similarity, search_mode }` |
| PUT | `/{id}/sync` | Query: `sync_type=replace\|complete`（Web） |
| GET | `/embedding_model` | 向量模型 |
| GET | `/model` | LLM 列表 |
| PUT | `/batch_delete` | `{ id_list }` |
| PUT | `/batch_move` | `{ id_list, folder_id }` |
| POST | `/import_knowledge` | multipart `file` |

### Workflow knowledge extras

| Method | Path | 说明 |
|--------|------|------|
| GET | `/{id}/workflow` | 入库工作流详情（`work_flow`） |
| PUT | `/{id}/workflow` | 保存入库图：`{ work_flow: { nodes, edges } }` |
| PUT | `/{id}/publish` | 发布入库工作流 |
| POST | `/{id}/debug` | 调试 |
| POST | `/{id}/upload_document` | 上传文档触发入库流 |
| GET | `/{id}/workflow/export` | 导出 `.kbwf` |
| POST | `/{id}/workflow/import` | multipart `file`（`.kbwf`）；**会覆盖**当前库工作流 |

脚本：

| 操作 | 脚本 |
|------|------|
| 创建 | `create_knowledge.py --kind workflow` |
| 查看 | `get_knowledge.py` / `--with-workflow` |
| 改元数据 | `update_knowledge.py` |
| 改入库图 | `save_knowledge_workflow.py` |
| 发布 | `publish_knowledge.py` |
| 商店模板 | `download_kbwf_template.py` |
| 导入 `.kbwf` | `import_knowledge_workflow.py`（需 `--allow-overwrite`） |
| 导出 | `export_knowledge_workflow.py` |
| 删除 | `delete_knowledge.py`（`--confirm-name` + `--yes`） |

## Document

前缀：`.../knowledge/{KID}/document`

| Method | Path | 说明 |
|--------|------|------|
| GET | `` | 文档列表 |
| GET | `/{page}/{size}` | 分页 |
| GET | `/{doc_id}` | 详情 |
| PUT | `/{doc_id}` | 编辑；可含 `hit_handling_method`: `optimization`\|`directly_return` |
| DELETE | `/{doc_id}` | 删除 |
| POST | `/split` | 分段预览 multipart |
| GET | `/split_pattern` | 预设分段正则 |
| **PUT** | `/batch_create` | 按段落数组落库 |
| POST | `/web` | `{ source_url_list[], selector? }` |
| POST | `/qa` | QA 文件 |
| POST | `/table` | 表格文件 |
| PUT | `/batch_delete` | `{ id_list }` |
| PUT | `/batch_refresh` | `{ id_list, state_list }` |
| PUT | `/batch_cancel_task` | 取消任务 |

### batch_create 元素

```json
{
  "name": "string",
  "source_file_id": "string|optional",
  "paragraphs": [
    {
      "content": "string",
      "title": "string",
      "problem_list": [{ "id": "string", "content": "string" }],
      "is_active": true
    }
  ]
}
```

### split 示例（curl）

```bash
curl -X POST "{ADMIN_API}/workspace/{WS}/knowledge/{KID}/document/split" \
  -H "Authorization: Bearer YOUR_SYSTEM_API_KEY" \
  -F "file=@./manual.pdf" \
  -F "limit=4096" \
  -F "with_filter=true"
```

## Paragraph

前缀：`.../document/{DOC_ID}/paragraph`（CRUD、生成相关问题、批量迁移等）。字段核心：`content`, `title`, `is_active`, `problem_list`。

## curl：创建普通库

```bash
curl -X POST "{ADMIN_API}/workspace/default/knowledge/base" \
  -H "Authorization: Bearer YOUR_SYSTEM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "demo-kb",
    "folder_id": "default",
    "desc": "test",
    "embedding_model_id": "REPLACE_EMBEDDING_MODEL_ID"
  }'
```
