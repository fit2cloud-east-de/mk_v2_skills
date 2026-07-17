# Delegation 委派/委托

## 设计思路

主图只负责拆解与汇总；专业能力封装在子应用（application-node）。主从边界清晰，便于独立迭代专家 Agent。

## 场景

- 分层专家团队
- 检索专家+法务专家
- 多角色协作

## 要点

- 子应用 ID 真实可调用
- 主 Agent 定义交接字段
- 并行委派后 AND 汇总

## 用途（一句话）

主 Agent 拆任务，委派专用子 Agent，等待返回后汇总。

## MaxKB 落地要点

application-node 调用子应用；或 tool-workflow-lib-node。并行委派后 AND 汇聚。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。

```json
{
  "pattern_id": "18-delegation",
  "purpose": "主 Agent 拆任务，委派专用子 Agent，等待返回后汇总。",
  "scenarios": [
    "分层专家团队",
    "检索专家+法务专家",
    "多角色协作"
  ],
  "maxkb_mapping_notes": "application-node 调用子应用；或 tool-workflow-lib-node。并行委派后 AND 汇聚。",
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
            "name": "[拓扑审核] 18-delegation",
            "desc": "",
            "prologue": "你好，我是「委派协作助手」。\n主 Agent 拆任务，委派专用子 Agent，等待返回后汇总。\n\n你可以这样问我：\n- 把「竞品分析」拆给检索专家和分析专家后汇总\n- 委派专家协作完成一份调研摘要",
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
        "id": "n-decomp",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "主智能体拆解",
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
            "prompt": "拆解子任务并指定专家类型：{{开始.question}}",
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
        "id": "n-expert1",
        "type": "application-node",
        "x": 500,
        "y": 300,
        "properties": {
          "stepName": "委派检索专家",
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
        "id": "n-expert2",
        "type": "application-node",
        "x": 500,
        "y": 300,
        "properties": {
          "stepName": "委派分析专家",
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
            "application_id": "{{SUB_APP_ID_2}}",
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
        "id": "n-collect",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "主智能体汇总",
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
            "prompt": "检索专家：{{委派检索专家.result}}\n分析专家：{{委派分析专家.result}}\n汇总交付。",
            "dialogue_number": 1,
            "dialogue_type": "WORKFLOW",
            "is_result": true,
            "model_params_setting": {},
            "model_setting": {
              "reasoning_content_enable": true
            }
          }
        }
      }
    ],
    "edges": [
      {
        "id": "e1",
        "type": "app-edge",
        "sourceNodeId": "start-node",
        "targetNodeId": "n-decomp",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-decomp_left",
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
        "sourceNodeId": "n-decomp",
        "targetNodeId": "n-expert1",
        "sourceAnchorId": "n-decomp_right",
        "targetAnchorId": "n-expert1_left",
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
        "sourceNodeId": "n-decomp",
        "targetNodeId": "n-expert2",
        "sourceAnchorId": "n-decomp_right",
        "targetAnchorId": "n-expert2_left",
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
        "sourceNodeId": "n-expert1",
        "targetNodeId": "n-collect",
        "sourceAnchorId": "n-expert1_right",
        "targetAnchorId": "n-collect_left",
        "startPoint": {
          "x": 0,
          "y": 0
        },
        "endPoint": {
          "x": 0,
          "y": 0
        },
        "pointsList": [],
        "properties": {
          "condition": "AND"
        }
      },
      {
        "id": "e5",
        "type": "app-edge",
        "sourceNodeId": "n-expert2",
        "targetNodeId": "n-collect",
        "sourceAnchorId": "n-expert2_right",
        "targetAnchorId": "n-collect_left",
        "startPoint": {
          "x": 0,
          "y": 0
        },
        "endPoint": {
          "x": 0,
          "y": 0
        },
        "pointsList": [],
        "properties": {
          "condition": "AND"
        }
      }
    ]
  },
  "design_notes": "SUB_APP_ID / SUB_APP_ID_2 替换为真实子应用。",
  "design_thinking": "主图只负责拆解与汇总；专业能力封装在子应用（application-node）。主从边界清晰，便于独立迭代专家 Agent。",
  "key_points": [
    "子应用 ID 真实可调用",
    "主 Agent 定义交接字段",
    "并行委派后 AND 汇总"
  ]
}
```
