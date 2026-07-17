# Short-circuit 短路终止

## 设计思路

昂贵链路前先放廉价判定（检索置信、规则、缓存）。命中则 reply 直接 is_result 结束，未命中才进入长推理，控制成本与延迟。

## 场景

- 高置信检索直接返回答案
- 敏感词命中立即拒答
- 缓存命中跳过生成

## 要点

- 短路分支直接 reply 且 is_result
- 判定阈值/规则写清楚
- 未命中再进贵模型链路

## 用途（一句话）

早满足条件则提前结束，跳过昂贵后续节点。

## MaxKB 落地要点

condition-node 分流到 reply（is_result）即可短路；未命中再走长链路。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。

```json
{
  "pattern_id": "08-short-circuit",
  "purpose": "早满足条件则提前结束，跳过昂贵后续节点。",
  "scenarios": [
    "高置信检索直接返回答案",
    "敏感词命中立即拒答",
    "缓存命中跳过生成"
  ],
  "maxkb_mapping_notes": "condition-node 分流到 reply（is_result）即可短路；未命中再走长链路。",
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
            "name": "[拓扑审核] 08-short-circuit",
            "desc": "",
            "prologue": "你好，我是「短路早退助手」。\n早满足条件则提前结束，跳过昂贵后续节点。\n\n你可以这样问我：\n- 年假额度是多少？（高置信应直接答）\n- 解释一下复杂的跨部门审批链路",
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
        "id": "n-hit",
        "type": "search-knowledge-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "命中测试检索",
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
        "id": "n-direct",
        "type": "condition-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "是否可直答",
          "node_data": {
            "branch": [
              {
                "id": "br-hit",
                "type": "IF",
                "condition": "and",
                "conditions": [
                  {
                    "field": [
                      "n-hit",
                      "data"
                    ],
                    "compare": "is_not_null",
                    "value": ""
                  }
                ]
              },
              {
                "id": "br-miss",
                "type": "ELSE",
                "condition": "and",
                "conditions": []
              }
            ]
          }
        }
      },
      {
        "id": "n-short",
        "type": "reply-node",
        "x": 800,
        "y": 300,
        "properties": {
          "stepName": "短路直答",
          "node_data": {
            "reply_type": "content",
            "content": "根据检索直接返回：{{命中测试检索.data}}",
            "is_result": true
          }
        }
      },
      {
        "id": "n-deep",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "深度推理",
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
            "prompt": "检索不足，深入分析：{{开始.question}}",
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
        "targetNodeId": "n-hit",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-hit_left",
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
        "sourceNodeId": "n-hit",
        "targetNodeId": "n-direct",
        "sourceAnchorId": "n-hit_right",
        "targetAnchorId": "n-direct_left",
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
        "sourceNodeId": "n-direct",
        "targetNodeId": "n-short",
        "sourceAnchorId": "n-direct_br-hit_right",
        "targetAnchorId": "n-short_left",
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
        "sourceNodeId": "n-direct",
        "targetNodeId": "n-deep",
        "sourceAnchorId": "n-direct_br-miss_right",
        "targetAnchorId": "n-deep_left",
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
  "design_thinking": "昂贵链路前先放廉价判定（检索置信、规则、缓存）。命中则 reply 直接 is_result 结束，未命中才进入长推理，控制成本与延迟。",
  "key_points": [
    "短路分支直接 reply 且 is_result",
    "判定阈值/规则写清楚",
    "未命中再进贵模型链路"
  ]
}
```
