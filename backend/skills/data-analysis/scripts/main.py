"""数据分析技能执行脚本"""
import json
import pandas as pd
import numpy as np
from typing import Dict, Any


async def execute(
    data_file: str,
    analysis_type: str,
    target_column: str = None,
    output_format: str = "json",
    **kwargs
) -> Dict[str, Any]:
    """
    执行数据分析
    
    Args:
        data_file: 数据文件路径
        analysis_type: 分析类型(descriptive/trend/correlation)
        target_column: 目标列名(可选)
        output_format: 输出格式(json/csv/summary)
        **kwargs: 其他参数
    
    Returns:
        分析结果
    """
    try:
        # 读取数据文件
        if data_file.endswith('.csv'):
            df = pd.read_csv(data_file)
        elif data_file.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(data_file)
        else:
            return {
                "success": False,
                "error": f"不支持的文件格式: {data_file}"
            }
        
        # 数据基本信息
        result = {
            "success": True,
            "data_info": {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns)
            }
        }
        
        # 根据分析类型执行分析
        if analysis_type == "descriptive":
            result["analysis"] = _descriptive_analysis(df, target_column)
        
        elif analysis_type == "trend":
            result["analysis"] = _trend_analysis(df, target_column)
        
        elif analysis_type == "correlation":
            result["analysis"] = _correlation_analysis(df, target_column)
        
        else:
            return {
                "success": False,
                "error": f"不支持的分析类型: {analysis_type}"
            }
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _descriptive_analysis(df: pd.DataFrame, target_column: str = None) -> Dict[str, Any]:
    """描述性统计分析"""
    analysis = {
        "type": "descriptive",
        "summary": {}
    }
    
    # 数值列统计
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if target_column and target_column in numeric_cols:
        # 分析指定列
        col_data = df[target_column].dropna()
        analysis["summary"][target_column] = {
            "mean": float(col_data.mean()),
            "std": float(col_data.std()),
            "min": float(col_data.min()),
            "max": float(col_data.max()),
            "median": float(col_data.median()),
            "count": int(len(col_data))
        }
        analysis["insights"] = [
            f"{target_column} 的均值为 {analysis['summary'][target_column]['mean']:.2f}",
            f"标准差为 {analysis['summary'][target_column]['std']:.2f}",
            f"数据范围从 {analysis['summary'][target_column]['min']:.2f} 到 {analysis['summary'][target_column]['max']:.2f}"
        ]
    else:
        # 分析所有数值列
        for col in numeric_cols:
            col_data = df[col].dropna()
            analysis["summary"][col] = {
                "mean": float(col_data.mean()),
                "std": float(col_data.std()),
                "min": float(col_data.min()),
                "max": float(col_data.max()),
                "median": float(col_data.median())
            }
        analysis["insights"] = [
            f"共分析了 {len(numeric_cols)} 个数值列",
            "详细统计信息见 summary 部分"
        ]
    
    # 分类列统计
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    if categorical_cols:
        analysis["categorical"] = {}
        for col in categorical_cols[:3]:  # 只显示前3个
            value_counts = df[col].value_counts().head(5)
            analysis["categorical"][col] = {
                "unique_values": int(df[col].nunique()),
                "top_values": value_counts.to_dict()
            }
    
    return analysis


def _trend_analysis(df: pd.DataFrame, target_column: str = None) -> Dict[str, Any]:
    """趋势分析"""
    analysis = {
        "type": "trend",
        "summary": {}
    }
    
    # 尝试找到日期列
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    if not date_cols:
        # 尝试从 object 类型中找到日期列
        for col in df.select_dtypes(include=['object']).columns:
            try:
                pd.to_datetime(df[col].head(100))
                date_cols.append(col)
            except:
                pass
    
    if not date_cols:
        analysis["insights"] = ["未找到日期列,无法进行趋势分析"]
        return analysis
    
    date_col = date_cols[0]
    analysis["date_column"] = date_col
    
    # 选择数值列进行分析
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if target_column:
        cols_to_analyze = [c for c in numeric_cols if c == target_column]
    else:
        cols_to_analyze = numeric_cols[:3]
    
    # 转换日期并排序
    df_copy = df.copy()
    df_copy[date_col] = pd.to_datetime(df_copy[date_col])
    df_copy = df_copy.sort_values(date_col)
    
    for col in cols_to_analyze:
        col_data = df_copy[col].dropna()
        
        # 计算增长率
        if len(col_data) > 1:
            first_val = col_data.iloc[0]
            last_val = col_data.iloc[-1]
            growth_rate = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0
        else:
            growth_rate = 0
        
        # 计算移动平均(5期)
        if len(col_data) >= 5:
            ma5 = col_data.rolling(window=5, min_periods=1).mean().iloc[-1]
        else:
            ma5 = col_data.mean()
        
        analysis["summary"][col] = {
            "first_value": float(first_val),
            "last_value": float(last_val),
            "growth_rate": round(growth_rate, 2),
            "moving_average_5": round(ma5, 2)
        }
    
    analysis["insights"] = [
        f"使用 {date_col} 作为时间轴",
        f"分析了 {len(cols_to_analyze)} 个指标的趋势"
    ]
    
    if cols_to_analyze:
        col = cols_to_analyze[0]
        if col in analysis["summary"]:
            growth = analysis["summary"][col]["growth_rate"]
            if growth > 10:
                analysis["insights"].append(f"{col} 呈现上升趋势,增长率为 {growth}%")
            elif growth < -10:
                analysis["insights"].append(f"{col} 呈现下降趋势,下降率为 {abs(growth)}%")
            else:
                analysis["insights"].append(f"{col} 趋势相对稳定")
    
    return analysis


def _correlation_analysis(df: pd.DataFrame, target_column: str = None) -> Dict[str, Any]:
    """相关性分析"""
    analysis = {
        "type": "correlation",
        "summary": {}
    }
    
    # 选择数值列
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) < 2:
        analysis["insights"] = ["数值列少于2个,无法进行相关性分析"]
        return analysis
    
    # 计算相关系数矩阵
    corr_matrix = df[numeric_cols].corr()
    
    if target_column and target_column in numeric_cols:
        # 分析目标列与其他列的相关性
        correlations = []
        for col in numeric_cols:
            if col != target_column:
                corr = corr_matrix.loc[target_column, col]
                if not pd.isna(corr):
                    correlations.append({
                        "variable": col,
                        "correlation": round(corr, 3),
                        "strength": _get_correlation_strength(abs(corr))
                    })
        
        # 按相关性绝对值排序
        correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        analysis["summary"]["target_correlations"] = correlations[:5]
        
        # 生成洞察
        strong_corr = [c for c in correlations if abs(c["correlation"]) >= 0.7]
        moderate_corr = [c for c in correlations if 0.4 <= abs(c["correlation"]) < 0.7]
        
        insights = []
        if strong_corr:
            strong_names = [c["variable"] for c in strong_corr]
            insights.append(f"与 {target_column} 强相关的变量: {', '.join(strong_names)}")
        if moderate_corr:
            moderate_names = [c["variable"] for c in moderate_corr]
            insights.append(f"与 {target_column} 中等相关的变量: {', '.join(moderate_names)}")
        
        analysis["insights"] = insights or ["未发现显著相关性"]
    else:
        # 返回相关系数矩阵的前10个最强相关
        corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                corr = corr_matrix.iloc[i, j]
                if not pd.isna(corr):
                    corr_pairs.append({
                        "variables": [col1, col2],
                        "correlation": round(corr, 3)
                    })
        
        corr_pairs.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        analysis["summary"]["top_correlations"] = corr_pairs[:10]
        
        if corr_pairs:
            top_corr = corr_pairs[0]
            analysis["insights"] = [
                f"最强相关: {top_corr['variables'][0]} 和 {top_corr['variables'][1]} (r={top_corr['correlation']})"
            ]
        else:
            analysis["insights"] = ["未发现显著相关性"]
    
    return analysis


def _get_correlation_strength(corr: float) -> str:
    """获取相关性强度描述"""
    if abs(corr) >= 0.7:
        return "强相关"
    elif abs(corr) >= 0.4:
        return "中等相关"
    elif abs(corr) >= 0.2:
        return "弱相关"
    else:
        return "几乎不相关"
