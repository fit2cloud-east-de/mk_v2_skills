# Chain-of-Thought 思维链

## 设计思路

不强制多节点，而在单次生成中要求分步写出中间推理再给结论。是串行拓扑的轻量特化，强调可解释。

## 场景

- 简单逻辑推理
- 小学应用题
- 需要可解释中间步骤的问答

## 要点

- 单节点即可；可开 reasoning_content
- 提示词要求「先步骤后结论」
- 难推理可升级为多节点串行 CoT

## 用途（一句话）

串行分步推理的轻量变种，思考步骤内嵌在同一生成中。

## MaxKB 落地要点

单 ai-chat-node 即可；打开 reasoning_content_enable。复杂时可拆成多个串行思考节点。

## 拓扑 JSON（供 AI / 脚本读取）

将 `work_flow` 填入应用后，替换占位符 `{{MODEL_ID}}` 等；坐标可忽略。

```json
{
  "pattern_id": "15-chain-of-thought",
  "purpose": "串行分步推理的轻量变种，思考步骤内嵌在同一生成中。",
  "scenarios": [
    "简单逻辑推理",
    "小学应用题",
    "需要可解释中间步骤的问答"
  ],
  "maxkb_mapping_notes": "单 ai-chat-node 即可；打开 reasoning_content_enable。复杂时可拆成多个串行思考节点。",
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
            "name": "[拓扑审核] 15-chain-of-thought",
            "desc": "",
            "prologue": "你好，我是「思维链推理助手」。\n串行分步推理的轻量变种，思考步骤内嵌在同一生成中。\n\n你可以这样问我：\n- 一步步推理：为什么检索不到相关段落？\n- 分步说明如何做命中测试",
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
        "id": "n-cot",
        "type": "ai-chat-node",
        "x": 400,
        "y": 300,
        "properties": {
          "stepName": "分步思考作答",
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
            "system": "你进行 Chain-of-Thought：先逐步推理，最后给出结论。",
            "prompt": "请一步步思考（写出中间步骤），再给出最终答案。\n问题：{{开始.question}}",
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
        "targetNodeId": "n-cot",
        "sourceAnchorId": "start-node_right",
        "targetAnchorId": "n-cot_left",
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
  "design_notes": "属于 Sequential 的轻量特化，不必强行多节点。",
  "design_thinking": "不强制多节点，而在单次生成中要求分步写出中间推理再给结论。是串行拓扑的轻量特化，强调可解释。",
  "key_points": [
    "单节点即可；可开 reasoning_content",
    "提示词要求「先步骤后结论」",
    "难推理可升级为多节点串行 CoT"
  ]
}
```
