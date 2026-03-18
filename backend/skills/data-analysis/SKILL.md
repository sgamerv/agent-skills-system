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
4. 调用scripts/main.py脚本完成数据输出

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

## 脚本调用

### 脚本路径
```
scripts/main.py
```

### 执行函数
```python
async def execute(
    data_file: str,
    analysis_type: str,
    target_column: str = None,
    output_format: str = "json",
    **kwargs
) -> dict
```

### 参数映射
| Workflow 参数 | 脚本参数 | 类型 | 必填 | 说明 |
|--------------|---------|------|-----|------|
| {data_file} | data_file | str | 是 | 数据文件路径 |
| {analysis_type} | analysis_type | str | 是 | 分析类型 |
| {target_column} | target_column | str | 否 | 目标列名 |
| {output_format} | output_format | str | 否 | 输出格式，默认 json |

### 返回格式
```json
{
  "success": true,
  "message": "数据分析技能执行验证成功",
  "tool_info": {
    "name": "data-analysis",
    "script_path": "/path/to/scripts/main.py",
    "script_directory": "/path/to/scripts"
  },
  "parameters": {
    "data_file": "sales.csv",
    "analysis_type": "描述性统计",
    "target_column": "revenue",
    "output_format": "json"
  }
}
```
