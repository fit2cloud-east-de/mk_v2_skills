# Branch 条件分支 If-Else / Switch

## 设计思路

用显式条件把流量切到不同子图，避免一个提示词塞满所有策略。Switch 用多条 IF/ELSE IF 表达离散意图桶。

## 场景

- FAQ vs 闲聊分流
- 按用户等级走不同策略
- 意图分类后路由

## 要点

- 锚点格式 nodeId_branchId_right
- ELSE 兜底不可省
- 条件字段引用 start/上游输出

## 用途（一句话）

按条件走不同出口；多分支近似 Switch。

## MaxKB 落地要点

condition-node 的 branch IF/ELSE IF/ELSE；也可 intent-node 多出口。边锚点 source=nodeId_branchId_right。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。

```json
{
  "pattern_id": "05-branch-if-else-switch",
  "purpose": "按条件走不同出口；多分支近似 Switch。",
  "scenarios": [
    "FAQ vs 闲聊分流",
    "按用户等级走不同策略",
    "意图分类后路由"
  ],
  "maxkb_mapping_notes": "condition-node 的 branch IF/ELSE IF/ELSE；也可 intent-node 多出口。边锚点 source=nodeId_branchId_right。",
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
            "name": "拓扑-分支判断",
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
        "id": "n-if",
        "type": "condition-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "意图分支",
          "node_data": {
            "branch": [
              {
                "id": "br-faq",
                "type": "IF",
                "condition": "and",
                "conditions": [
                  {
                    "field": [
                      "start-node",
                      "question"
                    ],
                    "compare": "contain",
                    "value": "怎么"
                  }
                ]
              },
              {
                "id": "br-else",
                "type": "ELSE",
                "condition": "and",
                "conditions": []
              }
            ]
          }
        }
      },
      {
        "id": "n-faq",
        "type": "search-knowledge-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "FAQ检索",
          "condition": "AND",
          "config": {
            "fields": [
              {
                "label": "检索结果",
                "value": "data"
              }
            ]
          },
          "node_data": {
            "knowledge_id_list": [
              "{{KNOWLEDGE_ID}}"
            ],
            "knowledge_setting": {
              "top_n": 3,
              "similarity": 0.6,
              "max_paragraph_char_number": 5000,
              "search_mode": "embedding"
            },
            "question_reference_address": [
              "start-node",
              "question"
            ],
            "show_knowledge": true,
            "search_scope_type": "custom",
            "search_scope_source": "knowledge"
          }
        }
      },
      {
        "id": "n-faq-ans",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "FAQ回答",
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
            "prompt": "检索：{{FAQ检索.data}}\n问：{{开始.question}}",
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
        "id": "n-chat",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "闲聊回答",
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
            "prompt": "友好地回复：{{开始.question}}",
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
        "targetNodeId": "n-if",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-if_left",
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
        "sourceNodeId": "n-if",
        "targetNodeId": "n-faq",
        "sourceAnchorId": "n-if_br-faq_right",
        "targetAnchorId": "n-faq_left",
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
        "sourceNodeId": "n-faq",
        "targetNodeId": "n-faq-ans",
        "sourceAnchorId": "n-faq_right",
        "targetAnchorId": "n-faq-ans_left",
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
        "sourceNodeId": "n-if",
        "targetNodeId": "n-chat",
        "sourceAnchorId": "n-if_br-else_right",
        "targetAnchorId": "n-chat_left",
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
  "design_notes": "Switch：多个 ELSE IF 分支即可。",
  "design_thinking": "用显式条件把流量切到不同子图，避免一个提示词塞满所有策略。Switch 用多条 IF/ELSE IF 表达离散意图桶。",
  "key_points": [
    "锚点格式 nodeId_branchId_right",
    "ELSE 兜底不可省",
    "条件字段引用 start/上游输出"
  ]
}
```
