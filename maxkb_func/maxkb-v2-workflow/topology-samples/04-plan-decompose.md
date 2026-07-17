# Plan 规划分解

## 设计思路

先让模型产出可执行计划（结构化步骤），再按步骤执行与综合。计划与执行职责分离，便于审查「做错了哪一步」。

## 场景

- 复杂多步任务
- 调研报告
- 操作手册式流程

## 要点

- 计划输出尽量 JSON/编号列表
- 执行器只跟计划走，少临时加戏
- 综合器负责可读终稿，不重新规划

## 用途（一句话）

先生成计划，再按计划执行，最后综合。

## MaxKB 落地要点

用多个 ai-chat-node 串行模拟 Planner→Executor→Synthesizer；可用 loop 按 plan 逐步执行。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。

```json
{
  "pattern_id": "04-plan-decompose",
  "purpose": "先生成计划，再按计划执行，最后综合。",
  "scenarios": [
    "复杂多步任务",
    "调研报告",
    "操作手册式流程"
  ],
  "maxkb_mapping_notes": "用多个 ai-chat-node 串行模拟 Planner→Executor→Synthesizer；可用 loop 按 plan 逐步执行。",
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
            "name": "[拓扑审核] 04-plan-decompose",
            "desc": "",
            "prologue": "你好，我是「规划分解助手」。\n先生成计划，再按计划执行，最后综合。\n\n你可以这样问我：\n- 帮我规划一次两天的客户拜访行程\n- 把上线发布拆成可执行计划并给出结果",
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
        "id": "n-planner",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "规划器",
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
            "prompt": "为任务制定有序步骤 JSON plan：{{开始.question}}",
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
        "id": "n-exec",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "执行器",
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
            "prompt": "按计划执行并产出中间结果。计划：{{规划器.answer}}\n问题：{{开始.question}}",
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
        "id": "n-synth",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "综合器",
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
            "prompt": "根据执行结果给出最终答案：{{执行器.answer}}",
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
        "targetNodeId": "n-planner",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-planner_left",
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
        "sourceNodeId": "n-planner",
        "targetNodeId": "n-exec",
        "sourceAnchorId": "n-planner_right",
        "targetAnchorId": "n-exec_left",
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
        "sourceNodeId": "n-exec",
        "targetNodeId": "n-synth",
        "sourceAnchorId": "n-exec_right",
        "targetAnchorId": "n-synth_left",
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
  "design_thinking": "先让模型产出可执行计划（结构化步骤），再按步骤执行与综合。计划与执行职责分离，便于审查「做错了哪一步」。",
  "key_points": [
    "计划输出尽量 JSON/编号列表",
    "执行器只跟计划走，少临时加戏",
    "综合器负责可读终稿，不重新规划"
  ]
}
```
