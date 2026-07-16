# Agent Sequential 流水线多智能体

## 设计思路

多智能体按角色串成流水线，每段输入是上段交付物。强调岗位职责与交接格式，而非单模型扮演所有角色。

## 场景

- 内容生产流水线
- 研究报告自动生成
- 客服质检链路

## 要点

- 每段 Agent 角色单一
- 段间交付格式固定
- 审核段可驳回（可加分支回写作）

## 用途（一句话）

多专职 Agent 串行流转：检索→分析→写作→审核。

## MaxKB 落地要点

每个阶段一个 application-node（或 ai-chat 扮演角色）；严格串行边。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。

```json
{
  "pattern_id": "19-agent-sequential",
  "purpose": "多专职 Agent 串行流转：检索→分析→写作→审核。",
  "scenarios": [
    "内容生产流水线",
    "研究报告自动生成",
    "客服质检链路"
  ],
  "maxkb_mapping_notes": "每个阶段一个 application-node（或 ai-chat 扮演角色）；严格串行边。",
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
            "name": "拓扑-流水线多智能体",
            "desc": "",
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
        "id": "n-retriever",
        "type": "application-node",
        "x": 500,
        "y": 300,
        "properties": {
          "stepName": "检索Agent",
          "condition": "AND",
          "config": {
            "fields": [
              {
                "label": "回答",
                "value": "answer"
              }
            ]
          },
          "node_data": {
            "application_id": "{{SUB_APP_ID}}",
            "question_reference_address": [
              "start-node",
              "question"
            ],
            "api_input_field_list": [],
            "user_input_field_list": [],
            "is_result": false
          }
        }
      },
      {
        "id": "n-analyst",
        "type": "application-node",
        "x": 500,
        "y": 300,
        "properties": {
          "stepName": "分析Agent",
          "condition": "AND",
          "config": {
            "fields": [
              {
                "label": "回答",
                "value": "answer"
              }
            ]
          },
          "node_data": {
            "application_id": "{{SUB_APP_ID_ANALYST}}",
            "question_reference_address": [
              "start-node",
              "question"
            ],
            "api_input_field_list": [],
            "user_input_field_list": [],
            "is_result": false
          }
        }
      },
      {
        "id": "n-writer",
        "type": "application-node",
        "x": 500,
        "y": 300,
        "properties": {
          "stepName": "写作Agent",
          "condition": "AND",
          "config": {
            "fields": [
              {
                "label": "回答",
                "value": "answer"
              }
            ]
          },
          "node_data": {
            "application_id": "{{SUB_APP_ID_WRITER}}",
            "question_reference_address": [
              "start-node",
              "question"
            ],
            "api_input_field_list": [],
            "user_input_field_list": [],
            "is_result": false
          }
        }
      },
      {
        "id": "n-reviewer",
        "type": "application-node",
        "x": 500,
        "y": 300,
        "properties": {
          "stepName": "审核Agent",
          "condition": "AND",
          "config": {
            "fields": [
              {
                "label": "回答",
                "value": "answer"
              }
            ]
          },
          "node_data": {
            "application_id": "{{SUB_APP_ID_REVIEWER}}",
            "question_reference_address": [
              "start-node",
              "question"
            ],
            "api_input_field_list": [],
            "user_input_field_list": [],
            "is_result": false
          }
        }
      },
      {
        "id": "n-out",
        "type": "reply-node",
        "x": 800,
        "y": 300,
        "properties": {
          "stepName": "流水线产出",
          "node_data": {
            "reply_type": "content",
            "content": "{{审核Agent.answer}}",
            "is_result": true
          }
        }
      }
    ],
    "edges": [
      {
        "id": "e1",
        "type": "app-edge",
        "sourceNodeId": "start-node",
        "targetNodeId": "n-retriever",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-retriever_left",
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
        "sourceNodeId": "n-retriever",
        "targetNodeId": "n-analyst",
        "sourceAnchorId": "n-retriever_right",
        "targetAnchorId": "n-analyst_left",
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
        "sourceNodeId": "n-analyst",
        "targetNodeId": "n-writer",
        "sourceAnchorId": "n-analyst_right",
        "targetAnchorId": "n-writer_left",
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
        "id": "e4",
        "type": "app-edge",
        "sourceNodeId": "n-writer",
        "targetNodeId": "n-reviewer",
        "sourceAnchorId": "n-writer_right",
        "targetAnchorId": "n-reviewer_left",
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
        "id": "e5",
        "type": "app-edge",
        "sourceNodeId": "n-reviewer",
        "targetNodeId": "n-out",
        "sourceAnchorId": "n-reviewer_right",
        "targetAnchorId": "n-out_left",
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
  "design_notes": "与单 Agent Sequential 区别：节点是子智能体而非普通步骤。",
  "design_thinking": "多智能体按角色串成流水线，每段输入是上段交付物。强调岗位职责与交接格式，而非单模型扮演所有角色。",
  "key_points": [
    "每段 Agent 角色单一",
    "段间交付格式固定",
    "审核段可驳回（可加分支回写作）"
  ]
}
```
