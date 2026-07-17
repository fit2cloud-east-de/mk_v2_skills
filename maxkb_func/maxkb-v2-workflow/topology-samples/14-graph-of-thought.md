# Graph-of-Thought 思维图

## 设计思路

允许推理节点多入多出、交叉引用，形成图而非纯树。适合多线索互相印证；须避免无控环。

## 场景

- 多线索交叉推理
- 案件/调研多证据链
- 互相引用的假设检验

## 要点

- 边表达依赖，允许多入多出
- 警惕环；需要环时改用 loop
- 汇聚前明确各节点贡献

## 用途（一句话）

推理单元为图节点，可多入多出、交叉传信，比树更自由。

## MaxKB 落地要点

用多条边表达任意依赖；汇合 AND/OR。比 ToT 允许「边」在非层级节点间传递。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。

```json
{
  "pattern_id": "14-graph-of-thought",
  "purpose": "推理单元为图节点，可多入多出、交叉传信，比树更自由。",
  "scenarios": [
    "多线索交叉推理",
    "案件/调研多证据链",
    "互相引用的假设检验"
  ],
  "maxkb_mapping_notes": "用多条边表达任意依赖；汇合 AND/OR。比 ToT 允许「边」在非层级节点间传递。",
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
            "name": "[拓扑审核] 14-graph-of-thought",
            "desc": "",
            "prologue": "你好，我是「思维图推理助手」。\n推理单元为图节点，可多入多出、交叉传信，比树更自由。\n\n你可以这样问我：\n- 交叉分析：客户投诉、产品缺陷与流程缺口的关系\n- 多线索推断这个故障可能原因",
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
        "id": "n1",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "线索节点Alpha",
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
            "prompt": "从角度Alpha分析：{{开始.question}}",
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
        "id": "n2",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "线索节点Beta",
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
            "prompt": "结合Alpha结果从Beta分析：{{线索节点Alpha.answer}}\n问题：{{开始.question}}",
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
        "id": "n3",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "线索节点Gamma",
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
            "prompt": "交叉Alpha与Beta：A={{线索节点Alpha.answer}} B={{线索节点Beta.answer}}",
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
        "id": "n4",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "图汇总结论",
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
            "prompt": "综合图中节点信息给出结论：{{线索节点Gamma.answer}}",
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
        "targetNodeId": "n1",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n1_left",
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
        "sourceNodeId": "start-node",
        "targetNodeId": "n2",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n2_left",
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
        "sourceNodeId": "n1",
        "targetNodeId": "n2",
        "sourceAnchorId": "n1_right",
        "targetAnchorId": "n2_left",
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
        "sourceNodeId": "n1",
        "targetNodeId": "n3",
        "sourceAnchorId": "n1_right",
        "targetAnchorId": "n3_left",
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
        "sourceNodeId": "n2",
        "targetNodeId": "n3",
        "sourceAnchorId": "n2_right",
        "targetAnchorId": "n3_left",
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
        "id": "e6",
        "type": "app-edge",
        "sourceNodeId": "n3",
        "targetNodeId": "n4",
        "sourceAnchorId": "n3_right",
        "targetAnchorId": "n4_left",
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
  "design_notes": "注意避免环导致死循环；若需环用 loop 显式控制。",
  "design_thinking": "允许推理节点多入多出、交叉引用，形成图而非纯树。适合多线索互相印证；须避免无控环。",
  "key_points": [
    "边表达依赖，允许多入多出",
    "警惕环；需要环时改用 loop",
    "汇聚前明确各节点贡献"
  ]
}
```
