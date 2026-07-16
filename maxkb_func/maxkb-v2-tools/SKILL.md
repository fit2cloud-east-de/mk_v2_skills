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
| 需 shell/CLI | **不行**（默认禁 subprocess）：改节点方案或运维开沙箱开关 |

## 脚本

| 脚本 | 用途 |
|------|------|
| `list_tools.py` | 列表（自动带 `folder_id`） |
| `get_tool.py` | 详情 |
| `create_tool.py` | 创建后强制 `is_active` |
| `debug_tool.py` | 调试 |
| `pylint_tool.py` | 检查 |
| `update_tool.py` / `delete_tool.py` | 更新 / **删除（仅用户明确要求 + 确认删除 + `--yes`）** |

Windows 建议 JSON 走文件，避免 PowerShell 转义：

```bash
python create_tool.py --name echo --code-file ./echo.py \
  --input-fields-file ./fields.json --yes

python debug_tool.py --code-file ./echo.py \
  --input-fields-file ./fields.json \
  --debug-fields-file ./debug.json
```

`list_tools` / 创建时 `folder_id` 默认 = workspace id。
