# 工作流异常处理规范

对照 MaxKB **2.10.3-lts**。编排智能体时，节点除了**正常右出线**，还可开**异常分支**（仅 §2 白名单的 4 类节点），把报错细节交给下游（指定回复 / AI / 工具·工单函数等），而不是整条流程直接挂掉。

---

## 1. 机制（先记住）

| 项 | 说明 |
|----|------|
| 开关 | 节点 `properties.enableException = true` |
| 正常边 | `sourceAnchorId = "{nodeId}_right"` |
| 异常边 | `sourceAnchorId = "{nodeId}_exception_right"`（界面橙色锚点） |
| 报错字段 | 开启后多出输出 **`exception_message`**（异常信息字符串） |
| 运行时 | 节点 `status=500` 且已开异常 → 写入 `exception_message`，设 `branch_id=exception`，**只走异常边**；未开则整条工作流失败中断 |
| 边匹配 | 异常边靠 `branch_id=exception` 对应 `{id}_exception_right`，与条件分支同一套锚点规则 |

---

## 2. 哪些节点能开「异常」（白名单，只有 4 类）

界面在「输出参数」右侧渲染异常开关，白名单来自 `NodeContainer.vue` 的 `exceptionNodeList`（2.10.3 / 2.10.6 一致，全项目无节点覆盖该默认值）：

| 能开（仅这 4 类） | 不能开（写了也关不掉） |
|-------------------|------------------------|
| `ai-chat-node`（AI 对话） | `tool-node`（工作流内自定义代码 / 函数工具） |
| `image-understand-node`（图像理解） | `tool-lib-node`（工具库）/ `tool-workflow-lib-node` |
| `image-generate-node`（图像生成） | `application-node`（子应用） |
| `video-understand-node`（视频理解） | `search-knowledge-node`、`condition-node`、`reply-node`、`loop-node`、`knowledge-write-node`、`form-node` 等其余全部节点 |

### 给「不能开」的节点写 `enableException` 会发生什么（Issue #2）

前端只有 `properties.enableException` 为真时才**画**橙色 `{id}_exception_right` 锚点和「异常信息」输出项，但面板里的**开关本身受白名单限制**（`v-if="exceptionNodeList.includes(type)"`）。于是界面出现无法收拾的状态：

| 现象 | 说明 |
|------|------|
| 画布多一个橙色锚点，还能拉线 | 与用户手动拖出来的同类节点不一致 |
| 输出参数多出「异常信息 `exception_message`」 | **可被下游引用**，像是节点真有这个输出 |
| **复制该节点，异常参数跟着复制** | 因为存在 `properties` 里，不是渲染态 |
| **界面无法关闭** | 该类节点没有开关可点，只能删节点重建或改 JSON |

因此：**白名单外禁止写 `enableException`**。同理，`exception_message` 一律不要手写进 `properties.config.fields`——它是开关的派生字段，手写会造成重复/幽灵输出项，且复制节点时被带走。

**脚本不替你兜底**：`save_workflow.py` 只处理分支锚点、height、`pointsList`，**不会**清理 `enableException` 或 `exception_message`。所以这类错误必须在**生成 / 保存前自检**：逐节点确认异常开关只落在白名单 4 类上，`config.fields` 里没有 `exception_message`，改了再调保存脚本。

---

## 3. 编排规范（怎么接）

### 推荐拓扑

```text
… → [AI对话 / 易失败节点] ──正常──→ 后续对话 / 业务节点
                         └──异常──→ 兜底节点（必接）
                                      ├─ reply-node：固定安抚 + 展示报错
                                      ├─ ai-chat-node：用报错润色给用户
                                      └─ tool-lib-node / tool-node：建工单、告警、记日志
```

### 必须遵守

1. **开了异常开关，就必须拉异常边**；否则失败时 `branch_id=exception` 找不到下游，等同无兜底。  
2. **正常边与异常边互斥**：一次运行只走其一，不要假设两边都会执行。  
3. **下游引用报错**用节点输出字段，不要臆造字段名：  
   - 模板：`{{节点显示名.exception_message}}`  
   - 引用数组：`["{nodeId}", "exception_message"]`  
4. **对用户**：兜底文案先说「这次没处理好」，再视需要附带 `exception_message`（生产可脱敏，调试可全文）。  
5. **对运维**：工单 / 函数入参带上 `exception_message`、用户问题、`chat_id`（若有），便于排查。  
6. **不要**只靠异常分支做「业务失败」（如工具返回 `ok=false`）；那种用条件节点。异常分支只管**节点抛错 / status=500**。  
7. 与 [topology-samples/07-retry](topology-samples/07-retry.md) 搭配时：异常 → 有限次重试 → 仍失败再 reply/工单；务必有次数上限。

### 下游节点怎么用报错

| 下游 | 做法 |
|------|------|
| **指定回复** `reply-node` | `content` 写：`抱歉，处理失败。详情：{{AI对话.exception_message}}`，并设为结果输出 |
| **AI 对话** | system/用户提示里引用 `exception_message`，要求「转成对用户友好的说明，勿暴露密钥/堆栈」 |
| **工具 / 工单函数** `tool-lib-node` | 入参用**字符串模板**传入报错，如 `"{{AI对话.exception_message}}"`（不要用引用数组塞 tool-lib） |

---

## 4. JSON 最小形状（脚本落地）

```json
{
  "nodes": [
    {
      "id": "ai-1",
      "type": "ai-chat-node",
      "properties": {
        "stepName": "AI对话",
        "enableException": true,
        "node_data": {},
        "config": {
          "fields": [{ "label": "AI 回答", "value": "answer" }]
        }
      }
    },
    {
      "id": "reply-fallback",
      "type": "reply-node",
      "properties": {
        "stepName": "异常兜底回复",
        "node_data": {
          "reply_type": "content",
          "content": "抱歉，当前无法完成请求。\n原因：{{AI对话.exception_message}}",
          "is_result": true
        }
      }
    }
  ],
  "edges": [
    {
      "sourceNodeId": "ai-1",
      "targetNodeId": "reply-fallback",
      "sourceAnchorId": "ai-1_exception_right",
      "targetAnchorId": "reply-fallback_left"
    }
  ]
}
```

正常对话另接：`sourceAnchorId: "ai-1_right"` → 业务下游。

开启后节点可被引用的异常字段：

| 字段 | 含义 |
|------|------|
| `exception_message` | 异常详情（= 运行时 `err_message`） |

调试 `details` 里该节点还会带 `enableException`、`err_message`、`status=500`。

---

## 5. 运行时行为

```text
节点执行抛错或结果 status=500
  ├─ enableException != true
  │    → 工作流 status=500，流式推 ERROR，停止后续节点
  └─ enableException == true
       → context.exception_message = err_message
       → context.branch_id = "exception"
       → NodeResult({ branch_id: "exception", exception: err_message })
       → 只调度 sourceAnchor = "{id}_exception_right" 的边
```

判定「断言/分支结果」：`NodeResult` 含 `branch_id` 即走分支匹配（与 condition 节点同一套边逻辑）。

---

## 6. 验收清单

- [ ] 易失败节点已 `enableException: true`，且节点类型在 §2 白名单内（工具 / 子应用不在此列）
- [ ] 存在 `_exception_right` → 兜底节点的边
- [ ] 没有任何节点把 `exception_message` 手写进 `config.fields`
- [ ] 兜底能读到 `{{…exception_message}}`（或工具入参已传入）
- [ ] 故意制造失败（错模型 / 工具抛错）时：用户仍收到兜底回复，且调试详情里该节点 `status=500`、下游兜底为成功
- [ ] 正常路径不被异常边误执行

---

*技能包文档；密钥勿写入本文件。*
