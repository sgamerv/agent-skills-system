---
name: research-presentation
description: 研究主题并生成演示文稿
version: 1.0.0
author: Agent Team
category: research
tags: [research, presentation, mcp]
mcp_tools: [web_search, summarize]
---

# 研究并生成演示文稿

## 执行步骤
1. 使用web_search tool获取关于{topic}的最新进展，搜索关键词包括"{topic} 最新趋势"、"{topic} 技术突破"、"{topic} 2024"
2. 使用summarize skill对搜索结果进行总结，提取关键信息和主要观点
3. 根据总结内容，使用PPT skill生成演示文稿，每个关键信息点作为一页PPT
4. 将生成的演示文稿文件路径返回给用户

## 使用场景
- 快速研究一个新主题
- 准备演示材料
- 生成技术报告
- 学术研究准备

## 参数说明
- topic: 研究主题（必填），例如"人工智能"、"区块链"、"量子计算"等
- detail_level: 详细程度（可选），可选值：简洁、标准、详细，默认为标准
- slide_count: 幻灯片数量（可选），默认为10页

## 输出说明
执行完成后，将返回：
- 研究总结：包含关键信息和主要观点
- 演示文稿文件：PPT格式的演示文稿文件路径
- 数据来源：列出所有参考的数据来源

## 注意事项
- web_search工具需要MCP集成支持
- 如果搜索结果不足，会自动扩展搜索关键词
- 演示文稿会自动生成封面、目录、内容页和总结页
- 支持中英文搜索和内容生成
