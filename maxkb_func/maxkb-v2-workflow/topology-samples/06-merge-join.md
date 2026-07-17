# Merge / Join 汇聚合并

## 设计思路

多证据/多工具先并行采集，再在 Join 节点做冲突消解与加权融合。AND 适合「必须齐套」；OR 适合「谁快用谁」。

## 场景

- 多源证据融合
- 并行工具结果汇总
- 多模态结果合并

## 要点

- 并行检索/生成后再汇聚
- AND=全到齐；OR=抢先完成
- 汇聚提示词要做去重与冲突说明

## 用途（一句话）

多条并行路径汇入同一节点，AND 全到齐 / OR 任一即可。

## MaxKB 落地要点

汇合边设置 properties.condition。AND=全部完成；OR=任一完成即继续。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。

```json
{
  "pattern_id": "06-merge-join",
  "purpose": "多条并行路径汇入同一节点，AND 全到齐 / OR 任一即可。",
  "scenarios": [
    "多源证据融合",
    "并行工具结果汇总",
    "多模态结果合并"
  ],
  "maxkb_mapping_notes": "汇合边设置 properties.condition。AND=全部完成；OR=任一完成即继续。",
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
            "name": "[拓扑审核] 06-merge-join",
            "desc": "",
            "prologue": "你好，我是「多源汇聚助手」。\n多条并行路径汇入同一节点，AND 全到齐 / OR 任一即可。\n\n你可以这样问我：\n- 同时查产品手册和制度库：远程办公申请怎么走？\n- 合并多来源后回答：年终奖发放时间",
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
        "id": "n-kb1",
        "type": "search-knowledge-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "库A检索",
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
        "id": "n-kb2",
        "type": "search-knowledge-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "库B检索",
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
        "id": "n-join",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "汇聚生成",
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
            "prompt": "A：{{库A检索.data}}\nB：{{库B检索.data}}\n合并回答：{{开始.question}}",
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
        "targetNodeId": "n-kb1",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-kb1_left",
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
        "targetNodeId": "n-kb2",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-kb2_left",
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
        "sourceNodeId": "n-kb1",
        "targetNodeId": "n-join",
        "sourceAnchorId": "n-kb1_right",
        "targetAnchorId": "n-join_left",
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
        "sourceNodeId": "n-kb2",
        "targetNodeId": "n-join",
        "sourceAnchorId": "n-kb2_right",
        "targetAnchorId": "n-join_left",
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
  "design_thinking": "多证据/多工具先并行采集，再在 Join 节点做冲突消解与加权融合。AND 适合「必须齐套」；OR 适合「谁快用谁」。",
  "key_points": [
    "并行检索/生成后再汇聚",
    "AND=全到齐；OR=抢先完成",
    "汇聚提示词要做去重与冲突说明"
  ]
}
```
