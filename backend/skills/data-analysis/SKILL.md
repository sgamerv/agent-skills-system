---
name: data-analysis
description: 数据分析技能,支持 CSV/Excel 数据处理和统计分析
version: 1.0.0
author: Agent Team
category: analysis
tags: [data, analysis, statistics]
requires: [pandas, numpy]
provides: [analysis-result]
can_call: [visualization, knowledge-qa-expert]

# Slot 定义
slots:
  - name: data_file
    type: file
    required: true
    description: "需要分析的数据文件(CSV/Excel格式)"
    prompt: "请提供需要分析的数据文件路径"
    validation:
      - file_extension: [".csv", ".xlsx", ".xls"]
      - max_size: "100MB"

  - name: analysis_type
    type: enum
    required: true
    description: "分析类型"
    prompt: "请选择分析类型"
    options:
      - descriptive: "描述性统计 - 计算均值、标准差、中位数等统计指标"
      - trend: "趋势分析 - 分析数据随时间的变化趋势"
      - correlation: "相关性分析 - 分析变量之间的相关性"

  - name: target_column
    type: string
    required: false
    description: "需要重点关注的目标列名"
    prompt: "请指定需要重点分析的列名(可选)"
    depends_on: [data_file]

  - name: output_format
    type: enum
    required: false
    description: "输出格式"
    prompt: "请选择输出格式"
    options:
      - json: "JSON 格式 - 结构化数据输出"
      - csv: "CSV 文件 - 表格数据输出"
      - summary: "摘要报告 - 文本报告格式"
    default_value: "json"
---

# 数据分析技能

## 技能目标
对结构化数据进行分析,生成统计报告,可调用其他 Skills 进行可视化或知识查询。

## 使用场景
- 分析销售数据、用户数据等结构化数据
- 生成统计报表和数据摘要
- 数据趋势分析和相关性分析
- 为可视化技能提供数据支持

## 执行步骤

### 步骤 1: 数据加载
1. 读取用户指定的数据文件(CSV/Excel)
2. 验证数据格式和完整性
3. 显示数据基本信息(行数、列数、列名等)

### 步骤 2: 数据预处理
1. 处理缺失值
2. 数据类型转换
3. 数据清洗和规范化

### 步骤 3: 数据分析
根据分析类型执行相应的分析:

#### 描述性统计
- 计算数值列的均值、标准差、最小值、最大值、中位数
- 计算分类列的频数统计
- 生成数据摘要表

#### 趋势分析
- 按时间维度聚合数据
- 计算增长率、移动平均等指标
- 识别趋势和周期性模式

#### 相关性分析
- 计算变量间的相关系数矩阵
- 识别强相关和弱相关变量
- 生成相关性热力图数据

### 步骤 4: 结果输出
根据用户选择的输出格式生成结果。

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

## 可选的 Skill 调用

### 调用 visualization Skill
当用户需要可视化结果时:
```
Skill调用: visualization
输入参数:
  - data_type: "chart"
  - data: 分析结果数据
  - chart_type: 图表类型
期望输出: 图表文件路径
```

### 调用 knowledge-qa-expert Skill
当分析结果需要额外知识支持时:
```
Skill调用: knowledge-qa-expert
输入参数:
  - query: 基于分析结果生成的查询问题
期望输出: 相关知识解释
```

## 注意事项
- 数据文件大小限制为 100MB
- 支持的文件格式: CSV, XLSX, XLS
- 对于大数据集,建议先进行采样分析
- 确保数据文件路径正确可访问
