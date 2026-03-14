"""数据可视化技能执行脚本"""
import json
import os
import uuid
from typing import Dict, Any
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端


async def execute(
    data: Dict[str, Any],
    chart_type: str,
    title: str = "数据可视化",
    output_format: str = "png",
    **kwargs
) -> Dict[str, Any]:
    """
    执行数据可视化
    
    Args:
        data: 可视化数据(JSON 格式)
        chart_type: 图表类型(line/bar/pie/scatter/heatmap)
        title: 图表标题
        output_format: 输出格式(png/pdf/svg)
        **kwargs: 其他参数
    
    Returns:
        可视化结果
    """
    try:
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 根据图表类型绘制
        if chart_type == "line":
            _draw_line_chart(ax, data)
        elif chart_type == "bar":
            _draw_bar_chart(ax, data)
        elif chart_type == "pie":
            _draw_pie_chart(ax, data)
        elif chart_type == "scatter":
            _draw_scatter_chart(ax, data)
        elif chart_type == "heatmap":
            _draw_heatmap(ax, data)
        else:
            return {
                "success": False,
                "error": f"不支持的图表类型: {chart_type}"
            }
        
        # 设置标题和标签
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # 添加图例(如果需要)
        if chart_type in ["line", "bar", "scatter"]:
            ax.legend()
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图表
        output_dir = "./output/charts"
        os.makedirs(output_dir, exist_ok=True)
        
        file_name = f"chart_{uuid.uuid4().hex[:8]}.{output_format}"
        file_path = os.path.join(output_dir, file_name)
        
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # 生成描述
        description = _generate_description(chart_type, data)
        
        return {
            "success": True,
            "file_path": file_path,
            "format": output_format,
            "title": title,
            "description": description,
            "chart_info": {
                "type": chart_type,
                "data_points": len(data.get("x", data.get("data", [])))
            }
        }
        
    except Exception as e:
        plt.close()
        return {
            "success": False,
            "error": str(e)
        }


def _draw_line_chart(ax, data):
    """绘制折线图"""
    x = data.get("x", [])
    y = data.get("y", [])
    xlabel = data.get("xlabel", "X 轴")
    ylabel = data.get("ylabel", "Y 轴")
    
    ax.plot(x, y, marker='o', linewidth=2, markersize=6)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, alpha=0.3)


def _draw_bar_chart(ax, data):
    """绘制柱状图"""
    categories = data.get("categories", data.get("x", []))
    values = data.get("values", data.get("y", []))
    ylabel = data.get("ylabel", "数值")
    
    # 设置颜色
    colors = plt.cm.Set3(range(len(categories)))
    
    bars = ax.bar(range(len(categories)), values, color=colors, alpha=0.8)
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.set_ylabel(ylabel, fontsize=12)
    
    # 在柱子上显示数值
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{val}', ha='center', va='bottom', fontsize=9)
    
    ax.grid(True, alpha=0.3, axis='y')


def _draw_pie_chart(ax, data):
    """绘制饼图"""
    labels = data.get("labels", [])
    values = data.get("values", [])
    
    # 设置颜色
    colors = plt.cm.Set3(range(len(labels)))
    
    # 绘制饼图
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        explode=[0.05 if i == 0 else 0 for i in range(len(labels))]
    )
    
    # 设置文本大小
    for text in texts:
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_color('white')
        autotext.set_fontweight('bold')


def _draw_scatter_chart(ax, data):
    """绘制散点图"""
    x = data.get("x", [])
    y = data.get("y", [])
    xlabel = data.get("xlabel", "X 轴")
    ylabel = data.get("ylabel", "Y 轴")
    
    ax.scatter(x, y, alpha=0.6, s=100, c='blue', edgecolors='black', linewidth=1)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # 添加趋势线
    if len(x) > 1:
        import numpy as np
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        ax.plot(x, p(x), "r--", alpha=0.8, linewidth=2, label='趋势线')


def _draw_heatmap(ax, data):
    """绘制热力图"""
    matrix = data.get("matrix", [])
    x_labels = data.get("x_labels", [])
    y_labels = data.get("y_labels", [])
    
    import numpy as np
    matrix = np.array(matrix)
    
    # 绘制热力图
    im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto')
    
    # 设置刻度
    ax.set_xticks(range(len(x_labels)))
    ax.set_yticks(range(len(y_labels)))
    ax.set_xticklabels(x_labels, rotation=45, ha='right')
    ax.set_yticklabels(y_labels)
    
    # 添加颜色条
    plt.colorbar(im, ax=ax)
    
    # 在每个格子中显示数值
    for i in range(len(y_labels)):
        for j in range(len(x_labels)):
            text = ax.text(j, i, f'{matrix[i, j]:.2f}',
                         ha="center", va="center", color="black", fontsize=9)


def _generate_description(chart_type: str, data: Dict[str, Any]) -> str:
    """生成图表描述"""
    descriptions = {
        "line": "折线图展示了数据随时间或类别的变化趋势,适合观察数据的变化规律。",
        "bar": "柱状图展示了不同类别之间的数值比较,适合对比各类别的大小。",
        "pie": "饼图展示了各类别的占比情况,适合表现整体的构成和分布。",
        "scatter": "散点图展示了两个变量之间的关系,适合观察数据的分布和相关性。",
        "heatmap": "热力图展示了矩阵数据的数值分布,使用颜色深浅表示数值大小。"
    }
    
    base_desc = descriptions.get(chart_type, "数据可视化图表")
    
    # 添加数据点信息
    if "x" in data or "data" in data:
        data_points = len(data.get("x", data.get("data", [])))
        base_desc += f"\n\n数据点数量: {data_points}"
    
    return base_desc
