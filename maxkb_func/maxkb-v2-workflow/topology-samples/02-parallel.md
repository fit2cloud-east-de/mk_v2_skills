# Parallel 并行

## 设计思路

同一输入同时激发多条独立计算路径，缩短墙钟时间；在汇合点统一叙事。设计时先定义「各路径职责不重叠」，再定 AND/OR 汇合语义。

## 场景

- 多视角分析后汇总
- 多知识库同时检索再融合
- 多风格草稿并行生成

## 要点

- 从同一 source 拉多条边即并行
- 汇合边设置 condition=AND 或 OR
- 路径提示词分工明确，避免重复劳动

## 用途（一句话）

同一上游扇出到多个下游同时执行，再汇合。

## MaxKB 落地要点

一源多下游即并行；汇合边 properties.condition=AND|OR。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。

```json
{
  "pattern_id": "02-parallel",
  "purpose": "同一上游扇出到多个下游同时执行，再汇合。",
  "scenarios": [
    "多视角分析后汇总",
    "多知识库同时检索再融合",
    "多风格草稿并行生成"
  ],
  "maxkb_mapping_notes": "一源多下游即并行；汇合边 properties.condition=AND|OR。",
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
            "name": "[拓扑审核] 02-parallel",
            "desc": "",
            "prologue": "你好，我是「并行多视角助手」。\n同一上游扇出到多个下游同时执行，再汇合。\n\n你可以这样问我：\n- 请同时摘要并提取这篇文章的关键词：……\n- 从风险与收益两个角度分析这个方案",
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
        "id": "n-sum",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "摘要路径",
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
            "prompt": "请摘要：{{开始.question}}",
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
        "id": "n-kw",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "关键词路径",
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
            "prompt": "请提取关键词：{{开始.question}}",
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
        "id": "n-merge",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "合并回答",
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
            "prompt": "摘要：{{摘要路径.answer}}\n关键词：{{关键词路径.answer}}\n综合作答。",
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
        "targetNodeId": "n-sum",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-sum_left",
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
        "targetNodeId": "n-kw",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-kw_left",
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
        "sourceNodeId": "n-sum",
        "targetNodeId": "n-merge",
        "sourceAnchorId": "n-sum_right",
        "targetAnchorId": "n-merge_left",
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
        "id": "e4",
        "type": "app-edge",
        "sourceNodeId": "n-kw",
        "targetNodeId": "n-merge",
        "sourceAnchorId": "n-kw_right",
        "targetAnchorId": "n-merge_left",
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
  "design_notes": "MaxKB 并行受线程池限制，注意下游汇合条件。",
  "design_thinking": "同一输入同时激发多条独立计算路径，缩短墙钟时间；在汇合点统一叙事。设计时先定义「各路径职责不重叠」，再定 AND/OR 汇合语义。",
  "key_points": [
    "从同一 source 拉多条边即并行",
    "汇合边设置 condition=AND 或 OR",
    "路径提示词分工明确，避免重复劳动"
  ]
}
```
