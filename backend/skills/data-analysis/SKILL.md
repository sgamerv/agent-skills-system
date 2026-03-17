---
name: data-analysis
description: 数据分析技能,支持 CSV/Excel 数据处理和统计分析
version: 2.0.0
author: Agent Team
category: analysis
tags: [data, analysis, statistics]
mcp_tools: []
---

# 数据分析技能

## 执行步骤
1. 读取用户提供的{data_file}数据文件（支持CSV/Excel格式，最大100MB）
2. 检查数据质量，处理缺失值和异常值，显示数据基本信息（行数、列数、列名等）
3. 根据{analysis_type}执行相应的分析：
   - 描述性统计：计算均值、标准差、中位数等统计指标
   - 趋势分析：分析数据随时间的变化趋势，计算增长率、移动平均等
   - 相关性分析：计算变量间相关系数，识别强相关和弱相关变量
4. 如果用户指定了{target_column}，则重点分析该列的数据特征
5. 根据{output_format}生成结果（JSON/CSV/摘要报告），默认为JSON
6. 如果用户需要可视化，调用visualization skill生成图表
7. 返回分析结果给用户

## 使用场景
- 分析销售数据、用户数据等结构化数据
- 生成统计报表和数据摘要
- 数据趋势分析和相关性分析
- 为可视化技能提供数据支持

## 参数说明
- data_file: 数据文件路径（必填）
- analysis_type: 分析类型（必填），可选值：描述性统计、趋势分析、相关性分析
- target_column: 目标列名（可选），如果未指定则分析所有列
- output_format: 输出格式（可选），默认为JSON，可选值：json、csv、summary

## 输出格式

### JSON 格式
```json
{
  "statistics": {
    "mean": 123.45,
    "std": 45.67,
    "min": 10.0,
    "max": 200.0,
    "median": 115.5
  },
  "insights": [
    "数据均值为 123.45,标准差为 45.67",
    "数据分布较为均匀,无显著异常值"
  ]
}
```

### CSV 格式
导出包含统计结果的 CSV 文件。

### 摘要报告格式
生成包含图表说明和关键发现的文本报告。

## 注意事项
- 数据文件大小限制为 100MB
- 支持的文件格式: CSV, XLSX, XLS
- 对于大数据集,建议先进行采样分析
- 确保数据文件路径正确可访问
