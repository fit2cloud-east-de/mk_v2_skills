# Adaptive Router 自适应路由

## 设计思路

入口用轻量分类器估计难度/类型，再挂到不同子拓扑（短链/并行/规划）。用路由换「一刀切大图」的成本。

## 场景

- 通用万能 Agent 调度入口
- 降本：简单题走短链
- 难题自动升级拓扑

## 要点

- 路由标签集合封闭（simple/complex/plan）
- 各出口挂接完整子拓扑
- 路由模型用小提示、低温度

## 用途（一句话）

按任务难度/资源动态选择简单串行、复杂并行或规划流程。

## MaxKB 落地要点

ai-chat 分类 + condition-node 多出口挂接不同子拓扑。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。

```json
{
  "pattern_id": "16-adaptive-router",
  "purpose": "按任务难度/资源动态选择简单串行、复杂并行或规划流程。",
  "scenarios": [
    "通用万能 Agent 调度入口",
    "降本：简单题走短链",
    "难题自动升级拓扑"
  ],
  "maxkb_mapping_notes": "ai-chat 分类 + condition-node 多出口挂接不同子拓扑。",
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
            "name": "拓扑-自适应路由",
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
        "id": "n-router",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "难度路由",
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
            "prompt": "判断任务难度 simple|complex|plan，只输出标签。问题：{{开始.question}}",
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
        "id": "n-r",
        "type": "condition-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "路由分支",
          "node_data": {
            "branch": [
              {
                "id": "br-simple",
                "type": "IF",
                "condition": "and",
                "conditions": [
                  {
                    "field": [
                      "n-router",
                      "answer"
                    ],
                    "compare": "contain",
                    "value": "simple"
                  }
                ]
              },
              {
                "id": "br-complex",
                "type": "ELSE IF",
                "condition": "and",
                "conditions": [
                  {
                    "field": [
                      "n-router",
                      "answer"
                    ],
                    "compare": "contain",
                    "value": "complex"
                  }
                ]
              },
              {
                "id": "br-plan",
                "type": "ELSE",
                "condition": "and",
                "conditions": []
              }
            ]
          }
        }
      },
      {
        "id": "n-simple",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "简单串行应答",
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
            "prompt": "{{开始.question}}",
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
        "id": "n-complex-a",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "复杂并行视角1",
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
            "prompt": "视角1：{{开始.question}}",
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
        "id": "n-complex-b",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "复杂并行视角2",
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
            "prompt": "视角2：{{开始.question}}",
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
        "id": "n-complex-m",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "复杂合并",
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
            "prompt": "合并：{{复杂并行视角1.answer}} | {{复杂并行视角2.answer}}",
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
        "id": "n-plan",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "规划型流程",
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
            "prompt": "先规划再答：{{开始.question}}",
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
        "targetNodeId": "n-router",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-router_left",
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
        "sourceNodeId": "n-router",
        "targetNodeId": "n-r",
        "sourceAnchorId": "n-router_right",
        "targetAnchorId": "n-r_left",
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
        "sourceNodeId": "n-r",
        "targetNodeId": "n-simple",
        "sourceAnchorId": "n-r_br-simple_right",
        "targetAnchorId": "n-simple_left",
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
        "sourceNodeId": "n-r",
        "targetNodeId": "n-complex-a",
        "sourceAnchorId": "n-r_br-complex_right",
        "targetAnchorId": "n-complex-a_left",
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
        "sourceNodeId": "n-r",
        "targetNodeId": "n-complex-b",
        "sourceAnchorId": "n-r_br-complex_right",
        "targetAnchorId": "n-complex-b_left",
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
        "sourceNodeId": "n-complex-a",
        "targetNodeId": "n-complex-m",
        "sourceAnchorId": "n-complex-a_right",
        "targetAnchorId": "n-complex-m_left",
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
        "id": "e7",
        "type": "app-edge",
        "sourceNodeId": "n-complex-b",
        "targetNodeId": "n-complex-m",
        "sourceAnchorId": "n-complex-b_right",
        "targetAnchorId": "n-complex-m_left",
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
        "id": "e8",
        "type": "app-edge",
        "sourceNodeId": "n-r",
        "targetNodeId": "n-plan",
        "sourceAnchorId": "n-r_br-plan_right",
        "targetAnchorId": "n-plan_left",
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
  "design_thinking": "入口用轻量分类器估计难度/类型，再挂到不同子拓扑（短链/并行/规划）。用路由换「一刀切大图」的成本。",
  "key_points": [
    "路由标签集合封闭（simple/complex/plan）",
    "各出口挂接完整子拓扑",
    "路由模型用小提示、低温度"
  ]
}
```
