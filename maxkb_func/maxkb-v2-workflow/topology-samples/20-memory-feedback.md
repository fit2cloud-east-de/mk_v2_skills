# Memory Feedback 记忆回流

## 设计思路

本轮产出写入**独立记忆**，下轮再读出参与推理，形成闭环。

**切勿把下面三者混为一谈**（详见 [nodes-reference.md](../nodes-reference.md)「历史记录 vs 节点历史轮次 vs 长期/会话记忆」）：

| 概念 | 是什么 | 不是什么 |
|------|--------|----------|
| `history_context` | 本会话**聊天记录**（聊过什么） | 不是独立记忆库 |
| AI 节点 `dialogue_number` | 该节点调用模型时**自动带上前 N 轮** | 不是记忆写入/读取 |
| 基本信息「长期记忆」开关 → `{{开始.memory}}` | 界面按钮开启的**独立记忆能力** | 不是 `history_context` |

记忆回流拓扑应围绕 **`memory`（或外置 DB/知识库）** 设计；`history_context` / `dialogue_number` 只作多轮连贯的辅助，不能替代记忆。

## 场景

- 持续陪伴/顾问 Agent（偏好、人设沉淀）
- 跨会话项目助理（事实/待办回流）
- 个性化偏好累积

## 要点

- 先确认已在**基本信息**开启长期记忆（`long_term_enable`），提示词读 `{{开始.memory}}`，而不是把 `history_context` 标成「记忆」
- 多轮连贯另用各 AI 节点的 `dialogue_number`（或显式引用 `history_context`）
- 写入内容脱敏、可摘要；勿把密钥写入记忆
- 若不用平台长期记忆，可用 tool/知识库做外置回流，但仍与聊天记录区分开

## 用途（一句话）

借助独立记忆（`memory` 或外置存储）写入再读出参与推理；与聊天记录、节点历史轮次分离。

## MaxKB 落地要点

1. **独立记忆**：基本信息打开长期记忆 → 开始节点出现 `memory` → prompt 用 `{{开始.memory}}`；平台负责记忆条目的维护。  
2. **聊天记录**：需要时引用 `{{开始.history_context}}` / `{{global.history_context}}`，仅表示本会话已聊内容。  
3. **节点历史轮次**：每个 `ai-chat-node`（等）配置 `dialogue_number`，控制该组件带入前几轮。  
4. **外置回流（可选）**：tool 写 DB/知识库，下轮再检索；不要写成「写 history_context」。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。  
落地前请在基本信息开启长期记忆，否则 `{{开始.memory}}` 为空。

```json
{
  "pattern_id": "20-memory-feedback",
  "purpose": "借助独立记忆（memory 或外置存储）写入再读出参与推理；与 history_context、dialogue_number 分离。",
  "scenarios": [
    "持续陪伴/顾问 Agent",
    "跨会话项目助理",
    "个性化偏好累积"
  ],
  "maxkb_mapping_notes": "独立记忆：base-node.long_term_enable + {{开始.memory}}。聊天记录：history_context。节点带历史轮次：dialogue_number。三者勿混用。外置回流可用 tool/知识库。",
  "placeholders": {
    "MODEL_ID": "工作区 LLM 模型 UUID",
    "KNOWLEDGE_ID": "知识库 UUID（按需）",
    "SUB_APP_ID": "子智能体/应用 UUID（委派用）"
  },
  "work_flow": {
    "nodes": [
      {
        "id": "base-node",
        "type": "base-node",
        "x": 100,
        "y": 100,
        "properties": {
          "stepName": "基本信息",
          "node_data": {
            "name": "[拓扑审核] 20-memory-feedback",
            "desc": "须开启长期记忆(long_term_enable)；memory≠history_context≠dialogue_number",
            "prologue": "你好，我是「记忆回流助手」。\n借助独立记忆（memory 或外置存储）写入再读出参与推理；与 history_context、dialogue_number 分离。\n\n你可以这样问我：\n- 记住我偏好简洁回答，然后介绍你自己\n- 根据记忆中的偏好推荐提问方式",
            "tts_type": "BROWSER",
            "file_upload_enable": false,
            "long_term_enable": true
          },
          "user_input_field_list": [],
          "api_input_field_list": []
        }
      },
      {
        "id": "start-node",
        "type": "start-node",
        "x": 100,
        "y": 300,
        "properties": {
          "stepName": "开始",
          "config": {
            "fields": [
              {
                "label": "用户问题",
                "value": "question"
              },
              {
                "label": "长期记忆",
                "value": "memory"
              }
            ],
            "globalFields": [
              {
                "label": "当前时间",
                "value": "time"
              },
              {
                "label": "历史聊天记录",
                "value": "history_context"
              },
              {
                "label": "对话 ID",
                "value": "chat_id"
              }
            ]
          }
        }
      },
      {
        "id": "n-read",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "读取记忆参与推理",
          "condition": "AND",
          "config": {
            "fields": [
              {
                "label": "回答",
                "value": "answer"
              },
              {
                "label": "思考",
                "value": "reasoning_content"
              }
            ]
          },
          "node_data": {
            "model_id": "{{MODEL_ID}}",
            "system": "你是助手。区分：memory=独立记忆；history_context=本会话聊天记录；勿混淆。",
            "prompt": "【独立记忆 memory】{{开始.memory}}\n【本会话聊天记录 history_context，仅供参考】{{开始.history_context}}\n当前问题：{{开始.question}}\n请优先依据独立记忆中的偏好/事实作答。",
            "dialogue_number": 2,
            "dialogue_type": "WORKFLOW",
            "is_result": false,
            "model_params_setting": {},
            "model_setting": {
              "reasoning_content_enable": true
            }
          }
        }
      },
      {
        "id": "n-ans",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "本轮回答",
          "condition": "AND",
          "config": {
            "fields": [
              {
                "label": "回答",
                "value": "answer"
              },
              {
                "label": "思考",
                "value": "reasoning_content"
              }
            ]
          },
          "node_data": {
            "model_id": "{{MODEL_ID}}",
            "system": "你是助手。",
            "prompt": "结合上游对独立记忆的整理作答：{{读取记忆参与推理.answer}}\n用户问题：{{开始.question}}",
            "dialogue_number": 2,
            "dialogue_type": "WORKFLOW",
            "is_result": true,
            "model_params_setting": {},
            "model_setting": {
              "reasoning_content_enable": true
            }
          }
        }
      },
      {
        "id": "n-write-mem",
        "type": "tool-node",
        "x": 600,
        "y": 300,
        "properties": {
          "stepName": "记忆回流占位",
          "condition": "AND",
          "config": {
            "fields": [
              {
                "label": "结果",
                "value": "result"
              }
            ]
          },
          "node_data": {
            "name": "记忆回流占位",
            "desc": "平台长期记忆由 long_term 能力维护；本节点仅示意外置回流。勿写入 history_context。",
            "code": "def main(q, a):\n    # 平台长期记忆：依赖 base-node.long_term_enable，读 {{开始.memory}}\n    # 外置回流：在此写 DB/知识库；禁止把聊天记录当成记忆库\n    return {'result': 'memory_feedback_noted'}\n",
            "input_field_list": [
              {
                "name": "q",
                "type": "string",
                "source": "reference",
                "value": [
                  "start-node",
                  "question"
                ],
                "is_required": true
              },
              {
                "name": "a",
                "type": "string",
                "source": "reference",
                "value": [
                  "n-ans",
                  "answer"
                ],
                "is_required": true
              }
            ],
            "is_result": false
          }
        }
      }
    ],
    "edges": [
      {
        "id": "e1",
        "type": "app-edge",
        "sourceNodeId": "start-node",
        "targetNodeId": "n-read",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-read_left",
        "properties": {}
      },
      {
        "id": "e2",
        "type": "app-edge",
        "sourceNodeId": "n-read",
        "targetNodeId": "n-ans",
        "sourceAnchorId": "n-read_right",
        "targetAnchorId": "n-ans_left",
        "properties": {}
      },
      {
        "id": "e3",
        "type": "app-edge",
        "sourceNodeId": "n-ans",
        "targetNodeId": "n-write-mem",
        "sourceAnchorId": "n-ans_right",
        "targetAnchorId": "n-write-mem_left",
        "properties": {}
      }
    ]
  },
  "design_notes": "memory（长期记忆开关）≠ history_context（聊天记录）≠ dialogue_number（节点保留前 N 轮）。回流读 memory；多轮连贯用 dialogue_number/history_context。",
  "design_thinking": "本轮产出进入独立记忆，下轮再读出参与推理。必须与聊天记录、节点历史轮次分离，避免记错层级。",
  "key_points": [
    "基本信息开启长期记忆后使用 {{开始.memory}}",
    "history_context 仅是本会话聊天记录",
    "dialogue_number 是各 AI 节点的前 N 轮上下文",
    "勿把密钥写入记忆"
  ]
}
```
