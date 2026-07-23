# 数据源工具（tool_type=DATA_SOURCE）CRUD 与创建规则

> 工作流知识库里的「数据源」有两类，勿混淆：  
> 1）内置节点：`data-source-local-node` / `data-source-web-node`（改图用 `save_knowledge_workflow.py`）  
> 2）**本文件**：工具库里的 **`tool_type=DATA_SOURCE`**，挂到知识库图上时 `properties.kind=data-source`

API 与普通工具同一前缀：`/workspace/{WS}/tool`。脚本在 `maxkb-v2-tools/scripts/`。

---

## 1. CRUD 怎么做

| 操作 | 脚本 | 要点 |
|------|------|------|
| **查列表** | `list_tools.py --tool-type DATA_SOURCE` | 可加 `--name` / `--folder-id`；或 `--all-list --scope WORKSPACE` |
| **查详情** | `get_tool.py --tool-id ID` | 看 `code` / `input_field_list` / `init_field_list` / `is_active` |
| **创建** | `create_tool.py --tool-type DATA_SOURCE ... --yes` | 见 §2；创建后脚本会尽量强制 `is_active=true` |
| **更新** | `update_tool.py --tool-id ID --body-json patch.json --yes` | 只传要改的字段；改密钥用 `init_params`（加密存储） |
| **删除** | `delete_tool.py --tool-id ID --confirm-name "确切名称" --yes` | 须用户明确要求 +「确认删除」+ 名称二次确认 |

```bash
# 列表
python list_tools.py --tool-type DATA_SOURCE --host HOST --workspace WS --api-key KEY

# 创建（推荐 code/字段走文件）
python create_tool.py --name "飞书云文档源" --tool-type DATA_SOURCE \
  --code-file ./ds_feishu.py \
  --init-fields-file ./init_fields.json \
  --input-fields-file ./input_fields.json \
  --yes --host HOST --workspace WS --api-key KEY

# 更新
python update_tool.py --tool-id TID --body-json ./patch.json --yes \
  --host HOST --workspace WS --api-key KEY

# 删除（确认删除后）
python delete_tool.py --tool-id TID --confirm-name "飞书云文档源" --yes \
  --host HOST --workspace WS --api-key KEY
```

挂到知识库工作流：拖入工具库节点，保证 `properties.kind = "data-source"`，并配置 `tool_lib_id`；图上仍须有固定 `knowledge-base-node` + `knowledge-write-node`。

---

## 2. 创建规则：必填 / 可省略

### 2.1 请求体字段（`POST .../tool`）

| 字段 | 必填？ | 可省略？ | 说明 |
|------|--------|----------|------|
| `name` | **是** | 否 | 显示名，≤64 |
| `code` | **是** | 否 | Python 源码字符串（见 §3） |
| `tool_type` | 建议显式 | 默认可成 CUSTOM | 数据源必须设 **`DATA_SOURCE`** |
| `folder_id` | 建议 | 可省略→脚本用 workspace id | 按「资源存放位置」三选一 |
| `desc` | 否 | **可省略** / `""` | |
| `input_field_list` | 否 | **可省略**→`[]` | 运行时/调试表单入参；也可全靠 `get_form_list` 动态出表单 |
| `init_field_list` | 否 | **可省略**→`[]` | 初始化配置（Token、Base URL 等）；有密钥时再配 |
| `init_params` | 创建时通常不传 | **可省略** | 创建后在「编辑」里填，后端 RSA 加密进库 |
| `is_active` | 否 | 可省略 | 后端 create 常落成 `false`；脚本会再 PUT 激活 |
| `icon` / `label` / `work_flow` | 否 | **可省略** | 数据源用不到 work_flow |
| `scope` | 否 | 可省略→`WORKSPACE` | |

**最小可创建体**（仅 name + code + tool_type + folder）：

```json
{
  "name": "最小数据源",
  "tool_type": "DATA_SOURCE",
  "folder_id": "<workspace_id>",
  "code": "def main(**kwargs):\n    return [{'name': 'a.md', 'content': 'hello'}]\n",
  "input_field_list": [],
  "init_field_list": [],
  "desc": ""
}
```

> 上面「最小」能入库工具库，但作为知识库**下载型**数据源时，平台更认 §3 的钩子函数；`main` 仅在未实现 `get_download_file_list` 时被调用（见下）。

### 2.2 `input_field_list` / `init_field_list` 元素（需要时）

常见键（与自定义工具相同，多余键一般可省略）：

| 键 | 建议 | 可省略 |
|----|------|--------|
| `name` 或 `field` | 变量名 | 否（有字段时） |
| `label` | 展示名 | 可用 name 顶上 |
| `type` / `input_type` | string、password 等 | 有默认时看 UI |
| `is_required` / `required` | 是否必填 | 默认可 false |
| `source` | `custom` / 引用 | 入参常用 `custom` |
| `default_value` | 默认 | **可省略** |

---

## 3. 代码约定（与执行引擎对齐）

运行时（`base_tool_lib_node`，`kind=data-source`）：

1. 合并 `init_field` 默认值 + 解密后的 `init_params` + 节点入参 + 调试/`data_source` 表单。  
2. 探测是否存在函数 **`get_download_file_list`**（注意拼写：是 **download**，不是 UI 模板里的 `get_down_file_list`）。  
3. **若存在**：对列表每一项调 **`download`**，要求返回  
   `{"file_bytes": ["<base64>", ...], "name": "文件名.ext"}`  
   平台再上传 File，最终节点输出 **`result` = A 形** `[{file_id, name}, ...]`（接文档提取）。  
4. **若不存在**：`exec_code(code, params)` 无指定函数名 → 取 locals **最后一个**函数执行。UI 默认模板最后是 `download`（且是 `pass`）→ 极易得到 `None` 进而报错。自写代码时要么实现完整下载钩子，要么只保留一个返回 A/B 形数据的入口函数。

可选辅助：`get_form_list` / `get_file_list`（懒加载树形选文件，仅影响调试/导入表单，不是发布硬条件）。

### 推荐下载型骨架

```python
def get_form_list(node, **kwargs):
    return [{
        "field": "file_list",
        "text_field": "name",
        "value_field": "token",
        "input_type": "Tree",
        "attrs": {"lazy": True, "fetch_list_function": "get_file_list"},
        "label": "选择文件",
    }]

def get_file_list(**kwargs):
    # 返回可选文件/文件夹列表；文件夹设 leaf=False
    return []

def get_download_file_list(**kwargs):
    # 必须从这个名字导出！返回待下载项 list
    file_list = kwargs.get("file_list") or []
    return [f for f in file_list if f.get("leaf", True)]

def download(**kwargs):
    item = kwargs.get("download_item") or {}
    # 拉取字节后 base64 分片；禁止把 None 放进 file_bytes
    import base64
    raw = b""  # TODO: 真实下载
    name = item.get("name") or "file.bin"
    if not raw:
        raise Exception(f"empty download: {name}")
    chunk = base64.b64encode(raw).decode("ascii")
    return {"file_bytes": [chunk], "name": name}
```

### 非下载型（直接吐文档/分段结构）

不实现 `get_download_file_list`，且**只定义一个**入口，例如：

```python
def main(**kwargs):
    # 接分段：B 形；接提取：不要走这条，应走下载型 A
    return [{"name": "from-api.md", "content": "# hi\n"}]
```

返回值仍须符合 [ingest-io-contracts.md](../maxkb-v2-knowledge/ingest-io-contracts.md) 的 A/B/C。

---

## 4. 错误：`argument should be a bytes-like object or ASCII string, not 'NoneType'`

这是 Python `base64.b64decode(None)`（或少数路径对 `None` 做 decode）的典型报错，**不是**网络 401 文案。在数据源/工具场景里优先查：

| 原因 | 位置 | 怎么处理 |
|------|------|----------|
| **`download()` 的 `file_bytes` 里含 `None`**，或某分片是 `None` | `base_tool_lib_node`：`b64decode(chunk)` | 保证每个 chunk 都是非空 base64 **字符串**；无内容就 `raise`，不要 `file_bytes=[None]` |
| **`download()` 返回了 `None`** / 缺 `file_bytes` | 同上 | 必须 `return {"file_bytes":[...], "name":"..."}` |
| **函数名写错**：只实现了 UI 模板的 `get_down_file_list`，平台找的是 **`get_download_file_list`** | 探测失败 → 误调最后一个函数（常为空的 `download`）→ 得到 `None` | 改成正确函数名并实现 |
| **`init_params` 为 `None` 却被 `rsa_long_decrypt`** | `rsa_util.rsa_long_decrypt` → `b64decode(message)` | 工具未配置初始化参数时，执行路径应跳过解密；若商店导入/脏数据导致异常路径，在编辑里保存一次合法 `init_params`（可 `{}` 对应字段），或去掉空的 encrypted 字段 |
| 模型 `credential` 等为 `None` 却解密 | 模型/应用侧 | 与数据源无关时检查模型密钥是否未配置 |

排查顺序：看知识库调试 `details` 里该工具节点的 `err_message` → 核对是否走了 download 分支 → 打印/调试 `download` 返回值 → 确认 `get_download_file_list` 拼写。

---

## 5. 与内置本地/Web 节点的分工

| | 本地/Web 节点 | DATA_SOURCE 工具 |
|--|---------------|------------------|
| 创建 | 画在知识库工作流里 | `create_tool.py --tool-type DATA_SOURCE` |
| 更新 | 改 `node_data` / 整图 save | `update_tool.py` |
| 删除 | 从图中删节点（非删工具库） | `delete_tool.py`（删库内工具） |
| 查询 | `get_knowledge.py --with-workflow` | `list_tools` / `get_tool` |

知识库发布仍要求：**至少一个** `kind=data-source` 起点（可以是本地、Web **或** 数据源工具）。
