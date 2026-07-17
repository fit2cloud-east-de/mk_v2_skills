# Retry 重试流

## 设计思路

把失败视为可恢复状态：成功短路退出，失败进入有限次重试，耗尽则兜底。与通用 Loop 的区别是语义绑定「同一动作直至成功」。

## 场景

- 不稳定 HTTP/工具调用
- 模型偶发空答重生成
- 排队资源暂时不可用

## 要点

- 成功条件可检测（status/关键字）
- 重试次数硬上限 + 失败 reply 兜底
- 工具尽量幂等，避免重复扣费副作用

## 用途（一句话）

失败后有限次再试；是循环的特化拓扑，强调退出条件与兜底。

## MaxKB 落地要点

condition 判成功 + loop 限次；也可用异常分支 enableException。务必设最大次数。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。

```json
{
  "pattern_id": "07-retry",
  "purpose": "失败后有限次再试；是循环的特化拓扑，强调退出条件与兜底。",
  "scenarios": [
    "不稳定 HTTP/工具调用",
    "模型偶发空答重生成",
    "排队资源暂时不可用"
  ],
  "maxkb_mapping_notes": "condition 判成功 + loop 限次；也可用异常分支 enableException。务必设最大次数。",
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
            "name": "[拓扑审核] 07-retry",
            "desc": "",
            "prologue": "你好，我是「失败重试助手」。\n失败后有限次再试；是循环的特化拓扑，强调退出条件与兜底。\n\n你可以这样问我：\n- 调用外部天气接口查询上海今天天气\n- 不稳定接口重试后给我最终结果",
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
        "id": "n-call",
        "type": "tool-node",
        "x": 600,
        "y": 300,
        "properties": {
          "stepName": "调用外部接口",
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
            "name": "调用外部接口",
            "desc": "",
            "code": "def main(q):\n    return {'result': 'success', 'status': 'success'}\n",
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
        "id": "n-check",
        "type": "condition-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "是否成功",
          "node_data": {
            "branch": [
              {
                "id": "br-ok",
                "type": "IF",
                "condition": "and",
                "conditions": [
                  {
                    "field": [
                      "n-call",
                      "result"
                    ],
                    "compare": "contain",
                    "value": "success"
                  }
                ]
              },
              {
                "id": "br-retry",
                "type": "ELSE",
                "condition": "and",
                "conditions": []
              }
            ]
          }
        }
      },
      {
        "id": "n-retry-loop",
        "type": "loop-node",
        "x": 500,
        "y": 300,
        "properties": {
          "stepName": "失败重试循环",
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
        "id": "n-ok",
        "type": "reply-node",
        "x": 800,
        "y": 300,
        "properties": {
          "stepName": "成功回复",
          "node_data": {
            "reply_type": "content",
            "content": "调用成功：接口返回 success。",
            "is_result": true
          }
        }
      },
      {
        "id": "n-fail",
        "type": "reply-node",
        "x": 800,
        "y": 300,
        "properties": {
          "stepName": "失败兜底",
          "node_data": {
            "reply_type": "content",
            "content": "多次重试仍失败，请稍后再试。",
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
        "targetNodeId": "n-call",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-call_left",
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
        "sourceNodeId": "n-call",
        "targetNodeId": "n-check",
        "sourceAnchorId": "n-call_right",
        "targetAnchorId": "n-check_left",
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
        "sourceNodeId": "n-check",
        "targetNodeId": "n-ok",
        "sourceAnchorId": "n-check_br-ok_right",
        "targetAnchorId": "n-ok_left",
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
        "sourceNodeId": "n-check",
        "targetNodeId": "n-retry-loop",
        "sourceAnchorId": "n-check_br-retry_right",
        "targetAnchorId": "n-retry-loop_left",
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
        "sourceNodeId": "n-retry-loop",
        "targetNodeId": "n-fail",
        "sourceAnchorId": "n-retry-loop_right",
        "targetAnchorId": "n-fail_left",
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
  "design_notes": "独立于通用 Loop：语义是「同一动作直到成功或耗尽」。",
  "design_thinking": "把失败视为可恢复状态：成功短路退出，失败进入有限次重试，耗尽则兜底。与通用 Loop 的区别是语义绑定「同一动作直至成功」。",
  "key_points": [
    "成功条件可检测（status/关键字）",
    "重试次数硬上限 + 失败 reply 兜底",
    "工具尽量幂等，避免重复扣费副作用",
    "ARRAY 循环源必须是真正的 list；字符串会被按字符迭代。骨架可用 NUMBER。"
  ]
}
```
