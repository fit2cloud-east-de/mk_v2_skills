# Tree-of-Thought 思维树

## 设计思路

同一问题并行长出多条推理路径（树的兄弟节点），最后由评判节点择优。路径间初期隔离，避免互相污染。

## 场景

- 逻辑推理
- 奥数/竞赛题
- 方案对比决策

## 要点

- 分支并行、提示词差异化
- 评判节点只做择优与理由
- 控制分支数量（常见 3）控成本

## 用途（一句话）

多分支并行推演多条解题路径，再择优。

## MaxKB 落地要点

并行多个 ai-chat（不同 system/prompt）+ AND 汇聚到评判节点。深层 ToT 可在每分支内再嵌套分支。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。

```json
{
  "pattern_id": "13-tree-of-thought",
  "purpose": "多分支并行推演多条解题路径，再择优。",
  "scenarios": [
    "逻辑推理",
    "奥数/竞赛题",
    "方案对比决策"
  ],
  "maxkb_mapping_notes": "并行多个 ai-chat（不同 system/prompt）+ AND 汇聚到评判节点。深层 ToT 可在每分支内再嵌套分支。",
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
            "name": "拓扑-TreeOfThought",
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
        "id": "n-b1",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "路径分支1",
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
            "prompt": "路径A解题：{{开始.question}}",
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
        "id": "n-b2",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "路径分支2",
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
            "prompt": "路径B解题：{{开始.question}}",
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
        "id": "n-b3",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "路径分支3",
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
            "prompt": "路径C解题：{{开始.question}}",
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
        "id": "n-vote",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "择优选择",
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
            "prompt": "比较三路径，选最优并说明理由。\nA:{{路径分支1.answer}}\nB:{{路径分支2.answer}}\nC:{{路径分支3.answer}}",
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
        "targetNodeId": "n-b1",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-b1_left",
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
        "targetNodeId": "n-b2",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-b2_left",
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
        "sourceNodeId": "start-node",
        "targetNodeId": "n-b3",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-b3_left",
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
        "sourceNodeId": "n-b1",
        "targetNodeId": "n-vote",
        "sourceAnchorId": "n-b1_right",
        "targetAnchorId": "n-vote_left",
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
        "sourceNodeId": "n-b2",
        "targetNodeId": "n-vote",
        "sourceAnchorId": "n-b2_right",
        "targetAnchorId": "n-vote_left",
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
        "id": "e6",
        "type": "app-edge",
        "sourceNodeId": "n-b3",
        "targetNodeId": "n-vote",
        "sourceAnchorId": "n-b3_right",
        "targetAnchorId": "n-vote_left",
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
  "design_thinking": "同一问题并行长出多条推理路径（树的兄弟节点），最后由评判节点择优。路径间初期隔离，避免互相污染。",
  "key_points": [
    "分支并行、提示词差异化",
    "评判节点只做择优与理由",
    "控制分支数量（常见 3）控成本"
  ]
}
```
