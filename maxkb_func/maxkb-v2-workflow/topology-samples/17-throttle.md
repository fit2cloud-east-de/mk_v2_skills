# Throttle 资源限流

## 设计思路

用批处理+串行批间推进，把理论上的高扇出并行压到配额内。图上表达「限流策略」，真正信号量可在工具内实现。

## 场景

- 批量数据处理
- API QPS 受限
- 多文件向量化排队

## 要点

- 切批大小对齐 API 配额
- 批间串行=天然限流
- 批内小并行需额外约束

## 用途（一句话）

控制并行/并发数量，避免工具超限；常见为「批内有限并行 + 批间串行」。

## MaxKB 落地要点

用 loop 串行批处理模拟限流；避免 start 直接扇出过多并行边。平台并行上限亦需考虑。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。

```json
{
  "pattern_id": "17-throttle",
  "purpose": "控制并行/并发数量，避免工具超限；常见为「批内有限并行 + 批间串行」。",
  "scenarios": [
    "批量数据处理",
    "API QPS 受限",
    "多文件向量化排队"
  ],
  "maxkb_mapping_notes": "用 loop 串行批处理模拟限流；避免 start 直接扇出过多并行边。平台并行上限亦需考虑。",
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
            "name": "拓扑-限流Throttle",
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
        "id": "n-split",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "切分批次",
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
            "prompt": "把任务切成每批≤N条的 JSON batches：{{开始.question}}",
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
        "id": "n-batch-loop",
        "type": "loop-node",
        "x": 500,
        "y": 300,
        "properties": {
          "stepName": "按批顺序处理(限并发)",
          "node_data": {
            "loop_type": "array",
            "array_reference_address": [
              "start-node",
              "question"
            ],
            "max_loop_count": 5,
            "note": "MaxKB 循环体内部再挂 loop-start / ai-chat / tool / loop-break；此处为拓扑示意"
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
        "id": "n-limited",
        "type": "tool-node",
        "x": 600,
        "y": 300,
        "properties": {
          "stepName": "限流工具调用",
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
            "name": "限流工具调用",
            "desc": "",
            "code": "def main(batch):\n    # 批内可小并行，批间串行，从而限制总并发\n    return {'result': batch}\n",
            "input_field_list": [
              {
                "name": "batch",
                "type": "string",
                "source": "reference",
                "value": [
                  "n-split",
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
        "id": "n-agg",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "聚合输出",
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
            "prompt": "合并各批结果输出。",
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
        "targetNodeId": "n-split",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-split_left",
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
        "sourceNodeId": "n-split",
        "targetNodeId": "n-batch-loop",
        "sourceAnchorId": "n-split_right",
        "targetAnchorId": "n-batch-loop_left",
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
        "sourceNodeId": "n-batch-loop",
        "targetNodeId": "n-limited",
        "sourceAnchorId": "n-batch-loop_right",
        "targetAnchorId": "n-limited_left",
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
        "sourceNodeId": "n-limited",
        "targetNodeId": "n-agg",
        "sourceAnchorId": "n-limited_right",
        "targetAnchorId": "n-agg_left",
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
  "design_notes": "真正信号量需在 tool 代码或外部队列实现。",
  "design_thinking": "用批处理+串行批间推进，把理论上的高扇出并行压到配额内。图上表达「限流策略」，真正信号量可在工具内实现。",
  "key_points": [
    "切批大小对齐 API 配额",
    "批间串行=天然限流",
    "批内小并行需额外约束"
  ]
}
```
