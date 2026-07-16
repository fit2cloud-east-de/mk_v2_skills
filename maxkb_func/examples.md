# End-to-End（脚本版，Python 3.11）

套件根见上级 [../SKILL.md](../SKILL.md)。本文件属于 **maxkb_func 执行层**。

**先完成套件根 §0**：锁定本机 `MK_PYTHON`（≥3.11）与 pip，再索取路径 A/B 与 HOST、WORKSPACE、普通用户 API_KEY（勿用管理员 Key；Key 勿写入 skills / `.env`）。

在 `maxkb_func/` 下（将 `{MK_PYTHON}` 换成用户确认的解释器）：

```bash
{MK_PYTHON} -m venv .venv311
# Windows: .venv311\Scripts\python.exe -m pip install -r scripts/requirements.txt
# Unix:    .venv311/bin/python -m pip install -r scripts/requirements.txt
```

统一用命令行参数传入连接信息（勿依赖本机私有配置文件）；`python` 一律换成已锁定的 `{MK_PYTHON}` 或 venv 内解释器：

```bash
{MK_PYTHON} scripts/list_workspaces.py \
  --host https://your-maxkb.example.com \
  --workspace MyWorkspace \
  --api-key YOUR_USER_KEY

{MK_PYTHON} maxkb-v2-workflow/scripts/validate_workflow_params.py \
  --host https://your-maxkb.example.com \
  --workspace MyWorkspace \
  --api-key YOUR_USER_KEY \
  --yes
```

写操作均需确认后加 `--yes`。**删除默认禁止**：仅当用户明确要求并确认删除后，才可执行 `delete_*.py`。联调脚本默认保留资源，勿加 `--cleanup` 除非用户要求清理。沙箱见 `SANDBOX.md`。

有 EMBEDDING 模型后再建库：

```bash
{MK_PYTHON} maxkb-v2-knowledge/scripts/list_embedding_models.py \
  --host HOST --workspace WS --api-key KEY
{MK_PYTHON} maxkb-v2-knowledge/scripts/create_knowledge.py \
  --host HOST --workspace WS --api-key KEY \
  --kind base --name faq --embedding-model-id EMBED_ID --yes
```
