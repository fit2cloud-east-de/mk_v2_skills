# Memory Feedback 记忆回流

## 设计思路

本轮产出写入记忆，下轮读取再推理，形成闭环。必须先裁定 session（history_context）还是长期存储，避免记错层级。

## 场景

- 持续陪伴/顾问 Agent
- 跨会话项目助理
- 个性化偏好累积

## 要点

- 先选 session 还是长期记忆
- 写入内容脱敏、可摘要
- 下轮读取路径与写入一致

## 用途（一句话）

输出写入记忆，下轮读取再参与推理；需区分 session 与长期记忆。

## MaxKB 落地要点

session：用 start 的 history_context / dialogue_number；长期：tool 写外部存储或写入知识库，下轮 search-knowledge。variable-assign 可暂存本轮摘要。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。

```json
{
  "pattern_id": "20-memory-feedback",
  "purpose": "输出写入记忆，下轮读取再参与推理；需区分 session 与长期记忆。",
  "scenarios": [
    "持续陪伴/顾问 Agent",
    "跨会话项目助理",
    "个性化偏好累积"
  ],
  "maxkb_mapping_notes": "session：用 start 的 history_context / dialogue_number；长期：tool 写外部存储或写入知识库，下轮 search-knowledge。variable-assign 可暂存本轮摘要。",
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
            "name": "拓扑-记忆回流",
            "desc": "评估用 session history_context 还是长期记忆存储",
            "prologue": "你好",
            "tts_type": "BROWSER",
            "file_upload_enable": false
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
            "system": "你是助手。",
            "prompt": "长期/会话记忆：{{开始.history_context}}\n（若有 memory 字段一并纳入）\n当前问题：{{开始.question}}",
            "dialogue_number": 1,
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
            "prompt": "结合记忆作答：{{读取记忆参与推理.answer}}",
            "dialogue_number": 1,
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
          "stepName": "写入记忆",
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
            "name": "写入记忆",
            "desc": "",
            "code": "def main(q, a):\n    # session：依赖平台 history；长期：写入外部 DB/知识库\n    return {'result': 'memory_updated'}\n",
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
        "startPoint": {
          "x": 0,
          "y": 0
        },
        "endPoint": {
          "x": 0,
          "y": 0
        },
        "pointsList": [],
        "properties": {}
      },
      {
        "id": "e2",
        "type": "app-edge",
        "sourceNodeId": "n-read",
        "targetNodeId": "n-ans",
        "sourceAnchorId": "n-read_right",
        "targetAnchorId": "n-ans_left",
        "startPoint": {
          "x": 0,
          "y": 0
        },
        "endPoint": {
          "x": 0,
          "y": 0
        },
        "pointsList": [],
        "properties": {}
      },
      {
        "id": "e3",
        "type": "app-edge",
        "sourceNodeId": "n-ans",
        "targetNodeId": "n-write-mem",
        "sourceAnchorId": "n-ans_right",
        "targetAnchorId": "n-write-mem_left",
        "startPoint": {
          "x": 0,
          "y": 0
        },
        "endPoint": {
          "x": 0,
          "y": 0
        },
        "pointsList": [],
        "properties": {}
      }
    ]
  },
  "design_notes": "选型：短对话用 session；跨天/跨设备用长期记忆（DB 或知识库）。勿把密钥写入记忆。",
  "design_thinking": "本轮产出写入记忆，下轮读取再推理，形成闭环。必须先裁定 session（history_context）还是长期存储，避免记错层级。",
  "key_points": [
    "先选 session 还是长期记忆",
    "写入内容脱敏、可摘要",
    "下轮读取路径与写入一致"
  ]
}
```
