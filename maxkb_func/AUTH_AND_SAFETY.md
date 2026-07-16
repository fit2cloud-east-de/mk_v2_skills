# Auth & Safety

隶属套件 [mk_v2_skills](../SKILL.md) → 执行层 `maxkb_func`。

## 0. 会话启动参数

Agent **必须先**完成套件根 [SKILL.md](../SKILL.md) §0，顺序摘要：

0. **沟通模式**：编程小白（novice）/ 专业（pro）— 见根 §0.0；后续表述深度据此调整  
1. **Python**：探测 → 无 3.11+ 则询问是否安装 → 锁定 `MK_PYTHON`/`MK_PIP`  
2. **路径**：A 先头脑风暴 / B 直接制作 — 见根 §0.2  
3. `HOST` / `WORKSPACE` / `API_KEY`（普通用户 Key）

选 A 时：设计获批前不做本层写操作。选 B 或设计已批：须已锁定 Python ≥ 3.11，再用连接三项落地。

**禁止使用管理员 / 超管账号的 Key。**  
**禁止把真实 Key 写入任何 skill / md / 示例 / `.env` 文件。**  
连接信息只通过脚本的 `--host` / `--workspace` / `--api-key`（或当次进程环境变量）传入。  
**禁止在用户未确认前擅自安装 Python。**  
**禁止未选沟通模式就默认用专业黑话对业务用户输出。**


鉴权头：

```http
Authorization: Bearer <由用户提供的普通用户 API_KEY>
```

## 1. 普通用户 API Key（管理端脚本用这个）

- 入口：登录用户头像 → **API Key 管理**（专业版/企业版）  
- 管理接口：`/admin/api/system/api_key`（需已登录用户；创建后把 secret 交给脚本）  
- 用途：调用 `/admin/api/**`（建应用/知识库/工具、保存工作流、发布、调试等）  
- 文档：https://maxkb.cn/docs/v2/user_manual/X-Pack/system_API/

社区版可能无系统 API Key；那时用该普通用户的登录 Token，逻辑相同——仍勿用管理员身份。

## 2. 应用 API Key（仅对话）

- 入口：智能体概览 → API Key，形如 `agent-...`  
- **只能**用于 `/chat/api/**`  
- 与「普通用户系统 API Key」不是同一种；管理脚本勿混用

## 3. 路径与工作空间

| 前缀 | 默认 | 用途 |
|------|------|------|
| Admin API | `/admin/api` | 管理类脚本 |
| Chat API | `/chat/api` | 生产对话 |

`WORKSPACE` 可为显示名或 UUID；客户端经 `/workspace/by_user` 解析。根目录 `folder_id` 通常等于 workspace UUID。

## 4. 删除资源（硬约束）

**默认禁止通过 API / 脚本删除任何 MaxKB 资源。**

| 规则 | 说明 |
|------|------|
| **禁止主动删除** | 用户未提出删除诉求时，不得调用删除接口，也不得跑 `delete_*.py` |
| **禁止顺手清理** | 不得因「测试完了 / 重建方便 / 换方案 / 整理环境」等理由擅自删应用、知识库、文档、工具、API Key 等 |
| **禁止隐式删除** | 联调、校验、导入、覆盖编排等流程默认**保留**资源；不得默认走会删资源的清理分支 |
| **仅当用户要求** | 用户明确说要删（或书面确认删除某资源）后，才可进入删除流程 |
| **二次确认 + `--yes`** | 即使用户要求删除，仍须列出将删对象（类型、名称/ID、影响），等用户回复「确认删除」后再带 `--yes` 执行 |

适用范围：智能体/应用、知识库、文档/段落、工具、应用 API Key，以及任何 `DELETE` / `batch_delete` 类管理端调用。裸 HTTP 与脚本一视同仁。

删除确认示例：

```markdown
## 删除确认（不可恢复）
- 环境：{HOST} / workspace={WS}（测试 / 正式）
- 将删除：{类型} `{名称或 ID}`
- 影响：{关联应用/检索/对话是否受影响}
- 不可恢复：是

请明确回复「确认删除」后继续；仅回复「确认」不够。
```

## 5. 写操作确认模板（创建 / 更新 / 发布）

```markdown
## 变更确认
- 环境：{HOST} / workspace={WS}（测试 / 正式）
- 操作：{CREATE|UPDATE|PUBLISH|BATCH}
- 资源：{类型与 ID/名称}
- 影响：{一句话}

**风险责任说明**：本 Skill 仅供参考。请优先在测试环境验证后再迁正式环境；误操作风险由操作方承担。

请回复「确认」后继续。
```

删除类操作请用 §4，不要用本节笼统「确认」带过。

## 6. 推荐顺序

```text
0. 沟通模式：编程小白 / 专业（锁定 MK_AUDIENCE）
1. 探测本机 Python；无 3.11+ 则询问是否安装；锁定 MK_PYTHON / MK_PIP
2. 路径二选一（A 头脑风暴 / B 直接制作）+ HOST / WORKSPACE / 普通用户 API_KEY
3. 若选 A：brainstorming → 设计获批 → 交接清单；若选 B：跳过
4. 用已锁定解释器：venv + pip install -r requirements.txt（不建项目 .env）
5. list_workspaces 自检
6. knowledge / tool / workflow 脚本
7. 生产对话改用应用 agent- Key
```

写操作必须 `--yes` 且已人工确认。**删除**另受 §4 约束：无用户明确要求则禁止删除。全程对用户说明深度遵循 MK_AUDIENCE。
