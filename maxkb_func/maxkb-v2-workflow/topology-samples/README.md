# 智能体工作流拓扑样本（topology-samples）

本目录为 **少样本示例**：用 AI 可读的 `work_flow` JSON 描述常见智能体拓扑，便于头脑风暴后选型，再映射到 MaxKB 节点落地。

> 这些 JSON 是**设计骨架**（含 MaxKB 真实 `type`），不是保证一键可发布的完整生产图；落地时需补全模型 ID、循环体内部细节、工具代码与锚点。  
> **AI 节点**：样本中的短 `system`/`prompt` 仅为占位；正式保存/发布前必须按 [nodes-reference.md](../nodes-reference.md)「AI 节点提示词规范」补全 **Role / 限制 / 输出 / 示例**。

## 样本一览

| 文件 | 拓扑 | 一句话用途 |
|------|------|------------|
| [01-sequential.md](01-sequential.md) | Sequential 串行 | 节点按固定顺序依次执行，前一步输出作为后一步输入。 |
| [02-parallel.md](02-parallel.md) | Parallel 并行 | 同一上游扇出到多个下游同时执行，再汇合。 |
| [03-loop.md](03-loop.md) | Loop 循环 | 对数组/次数重复执行同一子流程，可用 break/continue。 |
| [04-plan-decompose.md](04-plan-decompose.md) | Plan 规划分解 | 先生成计划，再按计划执行，最后综合。 |
| [05-branch-if-else-switch.md](05-branch-if-else-switch.md) | Branch 条件分支 If-Else / Switch | 按条件走不同出口；多分支近似 Switch。 |
| [06-merge-join.md](06-merge-join.md) | Merge / Join 汇聚合并 | 多条并行路径汇入同一节点，AND 全到齐 / OR 任一即可。 |
| [07-retry.md](07-retry.md) | Retry 重试流 | 失败后有限次再试；是循环的特化拓扑，强调退出条件与兜底。 |
| [08-short-circuit.md](08-short-circuit.md) | Short-circuit 短路终止 | 早满足条件则提前结束，跳过昂贵后续节点。 |
| [09-cache-branch.md](09-cache-branch.md) | Cache Branch 缓存分支 | 先查缓存；命中短路返回，未命中计算后再回写。 |
| [10-react.md](10-react.md) | ReAct 推理+行动 | Thought→Action→Observation 循环，直到可作答；循环与规划结合的经典范式。 |
| [11-self-plan-replan.md](11-self-plan-replan.md) | Self-Plan + Replan 动态重规划 | 先 Plan，执行中发现异常/信息不足则 Replan，再继续。 |
| [12-hierarchical-plan.md](12-hierarchical-plan.md) | Hierarchical Plan 分层规划 | 顶层总规划→中层子任务→底层工具执行，多级拆解。 |
| [13-tree-of-thought.md](13-tree-of-thought.md) | Tree-of-Thought 思维树 | 多分支并行推演多条解题路径，再择优。 |
| [14-graph-of-thought.md](14-graph-of-thought.md) | Graph-of-Thought 思维图 | 推理单元为图节点，可多入多出、交叉传信，比树更自由。 |
| [15-chain-of-thought.md](15-chain-of-thought.md) | Chain-of-Thought 思维链 | 串行分步推理的轻量变种，思考步骤内嵌在同一生成中。 |
| [16-adaptive-router.md](16-adaptive-router.md) | Adaptive Router 自适应路由 | 按任务难度/资源动态选择简单串行、复杂并行或规划流程。 |
| [17-throttle.md](17-throttle.md) | Throttle 资源限流 | 控制并行/并发数量，避免工具超限；常见为「批内有限并行 + 批间串行」。 |
| [18-delegation.md](18-delegation.md) | Delegation 委派/委托 | 主 Agent 拆任务，委派专用子 Agent，等待返回后汇总。 |
| [19-agent-sequential.md](19-agent-sequential.md) | Agent Sequential 流水线多智能体 | 多专职 Agent 串行流转：检索→分析→写作→审核。 |
| [20-memory-feedback.md](20-memory-feedback.md) | Memory Feedback 记忆回流 | 输出写入记忆，下轮读取再参与推理；需区分 session 与长期记忆。 |

## 分 md 固定结构

每个样本文件均包含：

1. **设计思路** — 为什么这样画拓扑、控制流意图  
2. **场景** — 典型业务适用面  
3. **要点** — 落地时必须盯住的约束与坑  
4. 用途 / MaxKB 落地要点 / **拓扑 JSON**（`design_thinking`、`scenarios`、`key_points` 字段亦写入 JSON，便于 Agent 解析）

## 如何使用

1. 用户要「做智能体」时，先按用途/场景在本表选型（或路径 A 头脑风暴时引用本目录）。
2. 打开对应分 md，复制 `work_flow` JSON，替换 `{{MODEL_ID}}` / `{{KNOWLEDGE_ID}}` / 子应用 ID，并**按提示词规范补全每个 AI 节点**。
3. 用 `save_workflow.py --workflow-json ...` 写入应用，再 `debug_chat` 验证。
4. 并行/汇聚务必设置边 `properties.condition`；循环务必设 `max_loop_count`。

## 与 MaxKB 节点对照（速查）

| 拓扑概念 | 常用 MaxKB 节点 |
|----------|-----------------|
| 串行 | 普通边 |
| 并行 / 汇聚 | 一源多边；汇合边 AND/OR |
| 分支 / Switch | `condition-node` / `intent-node` |
| 循环 / Retry / ReAct | `loop-node` + break/continue |
| 规划 / CoT | 多个或单个 `ai-chat-node` |
| 委派 / 流水线 Agent | `application-node` |
| 缓存 / 限流 / 记忆落库 | `tool-node`（+ 条件） |
| 检索短路 | `search-knowledge-node` + `condition-node` + `reply-node` |

详见上级 [nodes-reference.md](../nodes-reference.md)、[SKILL.md](../SKILL.md)。
