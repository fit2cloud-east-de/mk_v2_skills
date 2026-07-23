---
name: maxkb-v2-tools
description: >-
  MaxKB tool scripts (Python 3.11+): create/debug/update tools; sandbox limits.
  Use for 工具、自定义函数、tool-lib、subprocess、markitdown.
---

# MaxKB v2 Tools

写操作加 `--yes`。套件根：[../../SKILL.md](../../SKILL.md)。启动前先完成执行层 [../SKILL.md](../SKILL.md) §0（**普通用户** Key，禁止管理员 Key，Key 不进 skills）。  
**删除默认禁止**：未获用户明确要求时，禁止跑 `delete_tool.py` 或调用删除接口。  
沙箱：**必读** [SANDBOX.md](../SANDBOX.md)。


## 决策

| 场景 | 做法 |
|------|------|
| 无复用 | 工作流 `tool-node` |
| 通用 | `create_tool.py` → `tool-lib-node`（入参用 `{{节点.字段}}` 模板） |
| **知识库数据源工具** | `create_tool.py --tool-type DATA_SOURCE`；规则见 **[data-source-tools.md](data-source-tools.md)** |
| 需 shell/CLI | **不行**（默认禁 subprocess）：改节点方案或运维开沙箱开关 |
| **挂到工作流知识库入库** | `return` / `download` 产物必须是入库契约 **A/B/C** 之一（见 [ingest-io-contracts.md](../maxkb-v2-knowledge/ingest-io-contracts.md)）；工具对外字段永远是 `result` |

### 入库场景下的 `return` 形状（摘要）

| 接到 | `return` |
|------|----------|
| 文档内容提取 | `[{"file_id":"…","name":"…"}, …]`（下载型数据源由平台生成） |
| 文档分段 | `[{"name":"…","content":"…"}, …]` |
| 知识库写入 | `[{"name":"…","paragraphs":[{"content":"…",…}]}, …]` |

不要 `return` 一段自由文本却接到写入节点。

### `NoneType` + base64 报错（数据源常见）

`argument should be a bytes-like object or ASCII string, not 'NoneType'` → 多为 `b64decode(None)`：  
`download()` 的 `file_bytes` 含空、函数名写成 `get_down_file_list`（平台要 **`get_download_file_list`**）、或对 `None` 的 `init_params` 做 RSA 解密。详见 [data-source-tools.md](data-source-tools.md) §4。

## 脚本

| 脚本 | 用途 |
|------|------|
| `list_tools.py` | 列表；`--tool-type DATA_SOURCE` 筛数据源 |
| `get_tool.py` | 详情 |
| `create_tool.py` | 创建（含 `--tool-type DATA_SOURCE`）；创建后尽量强制 `is_active` |
| `debug_tool.py` | 调试 |
| `pylint_tool.py` | 检查 |
| `update_tool.py` | 更新（`--body-json` / `--code-file` / `--init-params-file`…） |
| `delete_tool.py` | **删除（明确要求 +「确认删除」+ `--confirm-name` + `--yes`）** |

Windows 建议 JSON 走文件，避免 PowerShell 转义：

```bash
python create_tool.py --name echo --code-file ./echo.py \
  --input-fields-file ./fields.json --yes

python create_tool.py --name "我的云盘源" --tool-type DATA_SOURCE \
  --code-file ./ds.py --init-fields-file ./init.json --yes

python list_tools.py --tool-type DATA_SOURCE --host HOST --workspace WS --api-key KEY

python debug_tool.py --code-file ./echo.py \
  --input-fields-file ./fields.json \
  --debug-fields-file ./debug.json
```

`list_tools` / 创建时传 `--folder-id`（用户选根目录时用 workspace id）。创建前须按执行层「资源存放位置」让用户三选一。
