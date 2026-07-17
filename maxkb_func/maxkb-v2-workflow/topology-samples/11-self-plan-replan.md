# Self-Plan + Replan 动态重规划

## 设计思路

初始 Plan 只是假设；执行反馈若暴露缺口则 Replan，用新计划覆盖旧计划继续。适合约束会变化的开放任务。

## 场景

- 旅游规划
- 项目方案
- 开放域多约束任务

## 要点

- 用显式标记触发 NEED_REPLAN
- Replan 覆盖当前计划再执行
- 总步数/重规划次数双上限

## 用途（一句话）

先 Plan，执行中发现异常/信息不足则 Replan，再继续。

## MaxKB 落地要点

Plan/Replan 用 ai-chat；执行用 tool 或子步骤；条件触发重规划；loop 控制总步数。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。

```json
{
  "pattern_id": "11-self-plan-replan",
  "purpose": "先 Plan，执行中发现异常/信息不足则 Replan，再继续。",
  "scenarios": [
    "旅游规划",
    "项目方案",
    "开放域多约束任务"
  ],
  "maxkb_mapping_notes": "Plan/Replan 用 ai-chat；执行用 tool 或子步骤；条件触发重规划；loop 控制总步数。",
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
            "name": "[拓扑审核] 11-self-plan-replan",
            "desc": "",
            "prologue": "你好，我是「动态重规划助手」。\n先 Plan，执行中发现异常/信息不足则 Replan，再继续。\n\n你可以这样问我：\n- 帮我做一份三天杭州自由行计划，预算 2000\n- 项目中途加了新约束，请重规划",
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
        "id": "n-plan0",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "初始Plan",
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
            "prompt": "用3条以内步骤给出计划 JSON 数组。目标：{{开始.question}}",
            "dialogue_number": 0,
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
        "id": "n-run",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "执行一步",
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
            "prompt": "按计划给出可执行的最终方案（完整输出）。计划：{{初始Plan.answer}}",
            "dialogue_number": 0,
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
        "id": "n-ok",
        "type": "condition-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "是否偏离/信息不足",
          "node_data": {
            "branch": [
              {
                "id": "br-replan",
                "type": "IF",
                "condition": "and",
                "conditions": [
                  {
                    "field": [
                      "n-run",
                      "answer"
                    ],
                    "compare": "contain",
                    "value": "NEED_REPLAN"
                  }
                ]
              },
              {
                "id": "br-cont",
                "type": "ELSE",
                "condition": "and",
                "conditions": []
              }
            ]
          }
        }
      },
      {
        "id": "n-replan",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "重规划Replan",
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
            "prompt": "根据执行反馈修订计划：{{执行一步.answer}}",
            "dialogue_number": 0,
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
        "id": "n-loop",
        "type": "loop-node",
        "x": 500,
        "y": 300,
        "properties": {
          "stepName": "计划执行循环",
          "node_data": {
            "loop_type": "NUMBER",
            "array_reference_address": [
              "start-node",
              "question"
            ],
            "max_loop_count": 5,
            "note": "MaxKB 循环体内部再挂 loop-start / ai-chat / tool / loop-break；此处为拓扑示意；已含最小 loop_body（loop-start + reply 占位），落地时替换循环体内真实节点。 骨架测通：用 NUMBER=2，避免 ARRAY 把字符串按字符迭代。",
            "array": [
              "start-node",
              "question"
            ],
            "number": 2,
            "loop_body": {
              "nodes": [
                {
                  "id": "loop-start-node",
                  "type": "loop-start-node",
                  "x": 480,
                  "y": 3340,
                  "properties": {
                    "stepName": "循环开始",
                    "showNode": true,
                    "config": {
                      "fields": [
                        {
                          "label": "index",
                          "value": "index"
                        },
                        {
                          "label": "item",
                          "value": "item"
                        }
                      ],
                      "globalFields": []
                    }
                  }
                },
                {
                  "id": "loop-inner-reply",
                  "type": "reply-node",
                  "x": 780,
                  "y": 3340,
                  "properties": {
                    "stepName": "循环体占位",
                    "config": {
                      "fields": [
                        {
                          "label": "内容",
                          "value": "answer"
                        }
                      ]
                    },
                    "node_data": {
                      "reply_type": "content",
                      "content": "【循环体占位】index={{循环开始.index}} item={{循环开始.item}}（落地时替换为真实子流程）",
                      "is_result": false
                    }
                  }
                }
              ],
              "edges": [
                {
                  "id": "e-loop-inner-1",
                  "type": "app-edge",
                  "sourceNodeId": "loop-start-node",
                  "targetNodeId": "loop-inner-reply",
                  "sourceAnchorId": "loop-start-node_right",
                  "targetAnchorId": "loop-inner-reply_left",
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
            }
          },
          "config": {
            "fields": [
              {
                "label": "循环结果",
                "value": "result"
              }
            ]
          }
        }
      },
      {
        "id": "n-done",
        "type": "reply-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "完成输出",
          "condition": "AND",
          "node_data": {
            "reply_type": "content",
            "content": "方案已在上一步输出。",
            "is_result": false
          },
          "config": {
            "fields": [
              {
                "label": "内容",
                "value": "answer"
              }
            ]
          }
        }
      }
    ],
    "edges": [
      {
        "id": "e1",
        "type": "app-edge",
        "sourceNodeId": "start-node",
        "targetNodeId": "n-plan0",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-plan0_left",
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
        "sourceNodeId": "n-plan0",
        "targetNodeId": "n-run",
        "sourceAnchorId": "n-plan0_right",
        "targetAnchorId": "n-run_left",
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
  "design_thinking": "初始 Plan 只是假设；执行反馈若暴露缺口则 Replan，用新计划覆盖旧计划继续。适合约束会变化的开放任务。",
  "key_points": [
    "用显式标记触发 NEED_REPLAN",
    "Replan 覆盖当前计划再执行",
    "总步数/重规划次数双上限",
    "ARRAY 循环源必须是真正的 list；字符串会被按字符迭代。骨架可用 NUMBER。",
    "骨架测通：主路径 plan→execute(is_result)；重规划环保留节点但默认不接线，避免空答/死循环"
  ]
}
```
