---
name: knowledge-qa-expert
description: 专业知识问答技能,支持基于 RAG 的文档检索和智能回答
version: 1.0.0
author: Agent Team
category: knowledge
tags: [qa, rag, search]
requires: [vector-db, embedding-model]
provides: [qa-result]
can_call: []

# Slot 定义
slots:
  - name: query
    type: string
    required: true
    description: "用户提出的问题"
    prompt: "请提出您的问题"
    validation:
      - min_length: 1

  - name: context
    type: string
    required: false
    description: "提供的上下文信息(可选)"
    prompt: "如果有额外的上下文信息,请提供(可选)"
---

# 知识问答专家技能

## 技能目标
为用户提供准确、相关的知识问答服务,通过检索增强生成(RAG)技术,从知识库中提取相关信息并生成高质量回答。

## 使用场景
- 用户询问特定领域的知识问题
- 需要基于文档的精准回答
- 需要引用来源的问答场景
- 可作为其他 Skills 的知识查询子任务

## 执行步骤

### 步骤 1: 理解用户查询
分析用户问题的核心意图和关键实体。

### 步骤 2: 向量检索
1. 使用 embedding 模型将问题向量化
2. 在向量数据库中检索最相关的文档片段
3. 选择 top-k 最相关的片段(默认 k=3)

### 步骤 3: 上下文组装
将检索到的文档片段与用户问题组合成上下文。

### 步骤 4: 生成回答
基于上下文生成准确、相关且引用明确的回答。

## 注意事项
- 当检索结果相关性较低时,明确告知用户
- 保持回答的客观性,避免添加未在文档中支持的信息
- 重要的回答应该引用来源文档

## 可用工具
- `vector_search`: 向量相似度检索
- `document_loader`: 文档加载和预处理
- `embedding_service`: 文本向量化服务

## 输出格式
```json
{
  "answer": "回答内容",
  "sources": ["来源1", "来源2"],
  "confidence": 0.95
}
```
