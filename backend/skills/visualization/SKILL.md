---
name: visualization
description: 数据可视化技能,将数据分析结果生成图表
version: 1.0.0
author: Agent Team
category: visualization
tags: [chart, plot, graph]
requires: [matplotlib, seaborn]
provides: [chart-file]
can_call: []

# Slot 定义
slots:
  - name: data
    type: object
    required: true
    description: "需要可视化的数据(JSON 格式)"
    prompt: "请提供需要可视化的数据"

  - name: chart_type
    type: enum
    required: true
    description: "图表类型"
    prompt: "请选择图表类型"
    options:
      - line: "折线图 - 适合展示趋势和变化"
      - bar: "柱状图 - 适合比较不同类别"
      - pie: "饼图 - 适合展示占比"
      - scatter: "散点图 - 适合展示相关性"
      - heatmap: "热力图 - 适合展示矩阵数据"

  - name: title
    type: string
    required: false
    description: "图表标题"
    prompt: "请输入图表标题(可选)"
    default_value: "数据可视化"

  - name: output_format
    type: enum
    required: false
    description: "输出文件格式"
    prompt: "请选择输出格式"
    options:
      - png: "PNG 图片格式"
      - pdf: "PDF 文档格式"
      - svg: "SVG 矢量格式"
    default_value: "png"
---

# 数据可视化技能

## 技能目标
将数据分析结果生成美观、信息丰富的图表,帮助用户直观理解数据。

## 使用场景
- 数据分析结果的可视化展示
- 报告和演示文稿中的图表生成
- 数据探索和洞察发现
- 其他 Skills 的可视化子任务

## 执行步骤

### 步骤 1: 数据解析
1. 解析输入的数据(JSON 格式)
2. 验证数据结构和完整性
3. 确定可视化所需的字段

### 步骤 2: 图表设计
根据图表类型和数据特征设计可视化方案:

#### 折线图
- 适合展示时间序列数据
- X 轴为时间/类别,Y 轴为数值
- 支持多条线的对比

#### 柱状图
- 适合比较不同类别的数值
- X 轴为类别,Y 轴为数值
- 支持分组柱状图

#### 饼图
- 适合展示占比关系
- 显示各类别的百分比
- 支持突出显示特定切片

#### 散点图
- 适合展示两个变量的关系
- X 轴和 Y 轴均为数值
- 可添加趋势线

#### 热力图
- 适合展示矩阵数据
- 使用颜色深浅表示数值大小
- 常用于相关性矩阵

### 步骤 3: 图表生成
1. 使用 Matplotlib/Seaborn 生成图表
2. 添加标题、坐标轴标签、图例
3. 设置颜色方案和样式
4. 优化布局和字体大小

### 步骤 4: 文件输出
1. 将图表保存为指定格式
2. 返回文件路径
3. 生成图表说明文本

## 输出格式
```json
{
  "file_path": "/path/to/chart.png",
  "format": "png",
  "title": "图表标题",
  "description": "图表描述和关键发现",
  "chart_info": {
    "type": "line",
    "data_points": 100,
    "series": 1
  }
}
```

## 输入数据示例

### 折线图数据
```json
{
  "x": ["一月", "二月", "三月", "四月", "五月"],
  "y": [100, 120, 115, 130, 145],
  "xlabel": "月份",
  "ylabel": "销售额"
}
```

### 柱状图数据
```json
{
  "categories": ["产品A", "产品B", "产品C"],
  "values": [150, 200, 180],
  "ylabel": "销量"
}
```

### 饼图数据
```json
{
  "labels": ["类别A", "类别B", "类别C", "其他"],
  "values": [40, 30, 20, 10]
}
```

### 散点图数据
```json
{
  "x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
  "y": [2.1, 3.9, 6.2, 7.8, 10.1, 12.3, 14.5, 16.2, 18.8, 20.5],
  "xlabel": "变量 X",
  "ylabel": "变量 Y"
}
```

## 注意事项
- 数据点数量不宜过多,建议少于 1000 个
- 颜色选择考虑色盲友好
- 图表标题和标签要清晰明了
- 输出文件保存时间限制为 24 小时

## 可用工具
- `matplotlib`: Python 绘图库
- `seaborn`: 统计可视化库
- `plotly`: 交互式图表库(可选)
