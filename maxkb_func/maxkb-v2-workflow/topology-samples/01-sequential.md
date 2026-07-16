# Sequential 串行

## 设计思路

把任务拆成固定流水线：每步只做一件事，输出明确交给下一步。优先保证可预测性与易调试，不为复杂而并行。

## 场景

- 标准 RAG 问答
- 文档摘要→润色→输出
- 单路径客服话术

## 要点

- 每节点单一职责；边方向唯一、无扇出扇入
- 中间结果用模板变量引用上游字段
- 最终节点 is_result=true，便于调试定位

## 用途（一句话）

节点按固定顺序依次执行，前一步输出作为后一步输入。

## MaxKB 落地要点

MaxKB 默认边连接即为串行；一源一下游即可。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。

```json
{
  "pattern_id": "01-sequential",
  "purpose": "节点按固定顺序依次执行，前一步输出作为后一步输入。",
  "scenarios": [
    "标准 RAG 问答",
    "文档摘要→润色→输出",
    "单路径客服话术"
  ],
  "maxkb_mapping_notes": "MaxKB 默认边连接即为串行；一源一下游即可。",
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
            "name": "拓扑-串行Sequential",
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
        "id": "n-retrieve",
        "type": "search-knowledge-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "知识检索",
          "condition": "AND",
          "config": {
            "fields": [
              {
                "label": "检索结果",
                "value": "data"
              }
            ]
          },
          "node_data": {
            "knowledge_id_list": [
              "{{KNOWLEDGE_ID}}"
            ],
            "knowledge_setting": {
              "top_n": 3,
              "similarity": 0.6,
              "max_paragraph_char_number": 5000,
              "search_mode": "embedding"
            },
            "question_reference_address": [
              "start-node",
              "question"
            ],
            "show_knowledge": true,
            "search_scope_type": "custom",
            "search_scope_source": "knowledge"
          }
        }
      },
      {
        "id": "n-answer",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "生成回答",
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
            "prompt": "检索：{{知识检索.data}}\n问题：{{开始.question}}",
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
        "targetNodeId": "n-retrieve",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-retrieve_left",
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
        "sourceNodeId": "n-retrieve",
        "targetNodeId": "n-answer",
        "sourceAnchorId": "n-retrieve_right",
        "targetAnchorId": "n-answer_left",
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
  "design_notes": "最基础拓扑，优先作为默认模板。",
  "design_thinking": "把任务拆成固定流水线：每步只做一件事，输出明确交给下一步。优先保证可预测性与易调试，不为复杂而并行。",
  "key_points": [
    "每节点单一职责；边方向唯一、无扇出扇入",
    "中间结果用模板变量引用上游字段",
    "最终节点 is_result=true，便于调试定位"
  ]
}
```
