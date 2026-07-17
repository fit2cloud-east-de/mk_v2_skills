# ReAct 推理+行动

## 设计思路

显式交替「思考 / 行动 / 观察」：思考决定是否调工具，观察回灌下一轮思考，直到可作答。限制轮次防止空转。

## 场景

- 联网问答
- 数学/代码解题
- 需工具探查的开放问答

## 要点

- Thought 输出约定是否 ACTION
- Observation 必须回灌下一轮
- 轮次上限，防止死循环

## 用途（一句话）

Thought→Action→Observation 循环，直到可作答；循环与规划结合的经典范式。

## MaxKB 落地要点

ai-chat(思考)+condition+tool(行动/观察)+loop；限制轮次。也可用 ai-chat 的 tool_ids/MCP 简化。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。

```json
{
  "pattern_id": "10-react",
  "purpose": "Thought→Action→Observation 循环，直到可作答；循环与规划结合的经典范式。",
  "scenarios": [
    "联网问答",
    "数学/代码解题",
    "需工具探查的开放问答"
  ],
  "maxkb_mapping_notes": "ai-chat(思考)+condition+tool(行动/观察)+loop；限制轮次。也可用 ai-chat 的 tool_ids/MCP 简化。",
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
            "name": "[拓扑审核] 10-react",
            "desc": "",
            "prologue": "你好，我是「推理行动助手」。\nThought→Action→Observation 循环，直到可作答；循环与规划结合的经典范式。\n\n你可以这样问我：\n- 查一下知识库后回答：如何开通 VPN？\n- 需要工具计算：12*37 等于多少",
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
        "id": "n-think",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "思考Thought",
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
            "prompt": "观察问题，决定是否调用工具。仅当必须调工具时输出标记 [[ACTION]]；否则不要出现该标记。\n问题：{{开始.question}}",
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
        "id": "n-need-act",
        "type": "condition-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "是否需要行动",
          "node_data": {
            "branch": [
              {
                "id": "br-act",
                "type": "IF",
                "condition": "and",
                "conditions": [
                  {
                    "field": [
                      "n-think",
                      "answer"
                    ],
                    "compare": "contain",
                    "value": "[[ACTION]]"
                  }
                ]
              },
              {
                "id": "br-fin",
                "type": "ELSE",
                "condition": "and",
                "conditions": []
              }
            ]
          }
        }
      },
      {
        "id": "n-act",
        "type": "tool-node",
        "x": 600,
        "y": 300,
        "properties": {
          "stepName": "行动Action",
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
            "name": "行动Action",
            "desc": "",
            "code": "def main(thought):\n    return {'result': 'observation: ...'}\n",
            "input_field_list": [
              {
                "name": "thought",
                "type": "string",
                "source": "reference",
                "value": [
                  "n-think",
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
        "id": "n-obs",
        "type": "tool-node",
        "x": 600,
        "y": 300,
        "properties": {
          "stepName": "观察Observation",
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
            "name": "观察Observation",
            "desc": "",
            "code": "def main(action_out):\n    return {'result': action_out}\n",
            "input_field_list": [
              {
                "name": "action_out",
                "type": "string",
                "source": "reference",
                "value": [
                  "n-act",
                  "result"
                ],
                "is_required": true
              }
            ],
            "is_result": false
          }
        }
      },
      {
        "id": "n-react-loop",
        "type": "loop-node",
        "x": 500,
        "y": 300,
        "properties": {
          "stepName": "ReAct循环",
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
        "id": "n-final",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "最终作答",
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
            "prompt": "基于思考给出答案。思考：{{思考Thought.answer}}\n问题：{{开始.question}}",
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
        "targetNodeId": "n-think",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-think_left",
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
        "sourceNodeId": "n-think",
        "targetNodeId": "n-need-act",
        "sourceAnchorId": "n-think_right",
        "targetAnchorId": "n-need-act_left",
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
        "sourceNodeId": "n-need-act",
        "targetNodeId": "n-act",
        "sourceAnchorId": "n-need-act_br-act_right",
        "targetAnchorId": "n-act_left",
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
        "sourceNodeId": "n-act",
        "targetNodeId": "n-obs",
        "sourceAnchorId": "n-act_right",
        "targetAnchorId": "n-obs_left",
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
        "sourceNodeId": "n-obs",
        "targetNodeId": "n-react-loop",
        "sourceAnchorId": "n-obs_right",
        "targetAnchorId": "n-react-loop_left",
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
        "id": "e7",
        "type": "app-edge",
        "sourceNodeId": "n-need-act",
        "targetNodeId": "n-final",
        "sourceAnchorId": "n-need-act_br-fin_right",
        "targetAnchorId": "n-final_left",
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
  "design_notes": "推荐 max_loop_count≤5。",
  "design_thinking": "显式交替「思考 / 行动 / 观察」：思考决定是否调工具，观察回灌下一轮思考，直到可作答。限制轮次防止空转。",
  "key_points": [
    "Thought 输出约定是否 ACTION",
    "Observation 必须回灌下一轮",
    "轮次上限，防止死循环",
    "ARRAY 循环源必须是真正的 list；字符串会被按字符迭代。骨架可用 NUMBER。"
  ]
}
```
