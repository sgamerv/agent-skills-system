#!/usr/bin/env python3
"""
简化的后端启动脚本
"""
import os
import sys
import uvicorn

def main():
    """启动后端服务"""
    print("启动后端FastAPI服务...")
    
    # 设置环境变量
    os.environ.setdefault("LOG_LEVEL", "INFO")
    
    # 启动服务
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()