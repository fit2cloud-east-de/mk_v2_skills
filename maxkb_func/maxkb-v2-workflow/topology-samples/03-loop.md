# Loop 循环

## 设计思路

把「重复同类动作」从展开成 N 个节点改为循环体，用计数/数组驱动。设计重点是循环变量、退出条件与单次副作用是否幂等。

## 场景

- 批量处理列表项
- 多轮工具调用直到完成
- 分页抓取直到空

## 要点

- 必须设置 max_loop_count
- 循环体内引用用 `{{循环开始.item}}` / `{{循环开始.index}}`（界面名），**禁止** `{{loop.item}}`（会报 loop is undefined）
- 外层用 `{{拆成列表.answer}}`、`{{逐步执行循环.result}}`、`{{汇总循环结果.answer}}` 等界面节点名
- 循环体内可配 loop-break / continue
- 循环变量与数组引用地址要正确（参数里的 array 用节点 id）

## 用途（一句话）

对数组/次数重复执行同一子流程，可用 break/continue。

## MaxKB 落地要点

使用 loop-node + loop-body；体内可用 loop-break-node / loop-continue-node。设 max_loop_count 防死循环。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。

```json
{
  "pattern_id": "03-loop",
  "purpose": "对数组/次数重复执行同一子流程，可用 break/continue。",
  "scenarios": [
    "批量处理列表项",
    "多轮工具调用直到完成",
    "分页抓取直到空"
  ],
  "maxkb_mapping_notes": "使用 loop-node + loop-body；体内可用 loop-break-node / loop-continue-node。设 max_loop_count 防死循环。",
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
            "name": "[拓扑审核] 03-loop",
            "desc": "",
            "prologue": "你好，我是「循环逐步执行助手」。\n对数组/次数重复执行同一子流程，可用 break/continue。\n\n你可以这样问我：\n- 把下面任务拆成步骤并逐步执行：整理本周例会纪要并分发\n- 逐条处理这 3 个工单：……",
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
        "id": "n-plan-items",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "拆成列表",
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
            "prompt": "把用户目标拆成 JSON 数组 steps：{{开始.question}}",
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
        "id": "n-loop",
        "type": "loop-node",
        "x": 500,
        "y": 300,
        "properties": {
          "stepName": "逐步执行循环",
          "node_data": {
            "loop_type": "ARRAY",
            "array_reference_address": [
              "n-plan-items",
              "answer"
            ],
            "max_loop_count": 5,
            "note": "循环体内用界面节点名引用，如 {{循环开始.item}}；勿写 {{loop.item}}（易报 loop is undefined）。array 引用拆成列表.answer。",
            "array": [
              "n-plan-items",
              "answer"
            ],
            "number": 1,
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
                      "is_result": true
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
          "stepName": "汇总循环结果",
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
            "prompt": "循环结果：{{逐步执行循环.result}}\n给出最终答复。",
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
        "targetNodeId": "n-plan-items",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-plan-items_left",
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
        "sourceNodeId": "n-plan-items",
        "targetNodeId": "n-loop",
        "sourceAnchorId": "n-plan-items_right",
        "targetAnchorId": "n-loop_left",
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
        "sourceNodeId": "n-loop",
        "targetNodeId": "n-final",
        "sourceAnchorId": "n-loop_right",
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
  "design_notes": "提示词/回复用界面节点名：{{循环开始.item}}、{{拆成列表.answer}}、{{汇总循环结果.answer}}。勿写 {{loop.item}}。array 引用用节点 id。",
  "design_thinking": "把「重复同类动作」从展开成 N 个节点改为循环体，用计数/数组驱动。设计重点是循环变量、退出条件与单次副作用是否幂等。",
  "key_points": [
    "必须设置 max_loop_count",
    "循环体内引用用 {{循环开始.item}} / {{循环开始.index}}，禁止 {{loop.xxx}}",
    "外层用 {{拆成列表.answer}}、{{逐步执行循环.result}}、{{汇总循环结果.answer}} 等界面名",
    "循环体内可配 loop-break / continue"
  ]
}
```
