# Cache Branch 缓存分支

## 设计思路

读缓存 → 分支：命中直接答；未命中生成 → 写回缓存。键设计（问题归一化）与 TTL 在工具层实现，图上只表达控制流。

## 场景

- 高频相同问法
- 昂贵工具结果复用
- FAQ 热点加速

## 要点

- 缓存键与问题归一化策略
- 命中短路；未命中写回
- 敏感内容勿缓存明文

## 用途（一句话）

先查缓存；命中短路返回，未命中计算后再回写。

## MaxKB 落地要点

tool-node 封装缓存读写；条件分支分流。缓存介质在工具代码中实现。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。

```json
{
  "pattern_id": "09-cache-branch",
  "purpose": "先查缓存；命中短路返回，未命中计算后再回写。",
  "scenarios": [
    "高频相同问法",
    "昂贵工具结果复用",
    "FAQ 热点加速"
  ],
  "maxkb_mapping_notes": "tool-node 封装缓存读写；条件分支分流。缓存介质在工具代码中实现。",
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
            "name": "拓扑-缓存分支",
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
        "id": "n-cache-get",
        "type": "tool-node",
        "x": 600,
        "y": 300,
        "properties": {
          "stepName": "读缓存",
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
            "name": "读缓存",
            "desc": "",
            "code": "def main(q):\n    # 伪：查本地/Redis；未命中返回 miss\n    return {'result': 'miss'}\n",
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
              }
            ],
            "is_result": false
          }
        }
      },
      {
        "id": "n-c",
        "type": "condition-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "缓存是否命中",
          "node_data": {
            "branch": [
              {
                "id": "br-hit",
                "type": "IF",
                "condition": "and",
                "conditions": [
                  {
                    "field": [
                      "n-cache-get",
                      "result"
                    ],
                    "compare": "not_contain",
                    "value": "miss"
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
        "id": "n-from-cache",
        "type": "reply-node",
        "x": 800,
        "y": 300,
        "properties": {
          "stepName": "缓存命中回复",
          "node_data": {
            "reply_type": "content",
            "content": "{{读缓存.result}}",
            "is_result": true
          }
        }
      },
      {
        "id": "n-gen",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "实时生成",
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
            "prompt": "无缓存，生成回答：{{开始.question}}",
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
        "id": "n-cache-set",
        "type": "tool-node",
        "x": 600,
        "y": 300,
        "properties": {
          "stepName": "写缓存",
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
            "name": "写缓存",
            "desc": "",
            "code": "def main(q, ans):\n    return {'result': 'cached'}\n",
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
                "name": "ans",
                "type": "string",
                "source": "reference",
                "value": [
                  "n-gen",
                  "answer"
                ],
                "is_required": true
              }
            ],
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
          "stepName": "输出生成结果",
          "node_data": {
            "reply_type": "content",
            "content": "{{实时生成.answer}}",
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
        "targetNodeId": "n-cache-get",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-cache-get_left",
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
        "sourceNodeId": "n-cache-get",
        "targetNodeId": "n-c",
        "sourceAnchorId": "n-cache-get_right",
        "targetAnchorId": "n-c_left",
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
        "sourceNodeId": "n-c",
        "targetNodeId": "n-from-cache",
        "sourceAnchorId": "n-c_br-hit_right",
        "targetAnchorId": "n-from-cache_left",
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
        "sourceNodeId": "n-c",
        "targetNodeId": "n-gen",
        "sourceAnchorId": "n-c_br-miss_right",
        "targetAnchorId": "n-gen_left",
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
        "sourceNodeId": "n-gen",
        "targetNodeId": "n-cache-set",
        "sourceAnchorId": "n-gen_right",
        "targetAnchorId": "n-cache-set_left",
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
        "sourceNodeId": "n-cache-set",
        "targetNodeId": "n-out",
        "sourceAnchorId": "n-cache-set_right",
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
  "design_thinking": "读缓存 → 分支：命中直接答；未命中生成 → 写回缓存。键设计（问题归一化）与 TTL 在工具层实现，图上只表达控制流。",
  "key_points": [
    "缓存键与问题归一化策略",
    "命中短路；未命中写回",
    "敏感内容勿缓存明文"
  ]
}
```
