#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def create_directories():
    """创建必要的目录"""
    from backend.config import settings
    
    directories = [
        settings.UPLOAD_DIR,
        settings.VECTOR_DB_PATH,
        settings.SKILLS_DIR,
        "./output/charts",
        "./data",
        "./logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ 创建目录: {directory}")


def test_redis_connection():
    """测试 Redis 连接"""
    from backend.config import settings
    try:
        import redis.asyncio as redis
        client = redis.from_url(settings.REDIS_URL)
        
        # 同步测试
        import redis as sync_redis
        sync_client = sync_redis.from_url(settings.REDIS_URL)
        sync_client.ping()
        print(f"✓ Redis 连接成功: {settings.REDIS_URL}")
        return True
    except Exception as e:
        print(f"✗ Redis 连接失败: {e}")
        return False


def test_llm_connection():
    """测试 LLM 连接"""
    from backend.config import settings
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            base_url=settings.XINFERENCE_URL,
            api_key="empty",
            model=settings.XINFERENCE_MODEL_UID
        )
        # 发送简单测试请求
        response = llm.invoke("测试连接")
        print(f"✓ LLM 连接成功: {settings.XINFERENCE_MODEL_UID}")
        return True
    except Exception as e:
        print(f"✗ LLM 连接失败: {e}")
        print("  提示: 请确保 Xinference 服务已启动并且模型已加载")
        return False


def scan_skills():
    """扫描并验证技能"""
    from backend.core.skill_manager import SkillRegistry
    from backend.config import settings
    
    try:
        registry = SkillRegistry(settings.SKILLS_DIR)
        skills = registry.list_skills()
        
        print(f"\n✓ 发现 {len(skills)} 个技能:")
        for skill_name in skills:
            metadata = registry.get_skill_metadata(skill_name)
            print(f"  - {skill_name}: {metadata.get('description', 'No description')}")
        
        return True
    except Exception as e:
        print(f"✗ 技能扫描失败: {e}")
        return False


def create_sample_data():
    """创建示例数据文件"""
    import pandas as pd
    import numpy as np
    
    # 创建示例销售数据
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    data = {
        'date': dates,
        'product': np.random.choice(['产品A', '产品B', '产品C'], len(dates)),
        'sales': np.random.randint(100, 1000, len(dates)),
        'revenue': np.random.randint(1000, 10000, len(dates)),
        'customers': np.random.randint(10, 100, len(dates))
    }
    
    df = pd.DataFrame(data)
    output_path = './data/sample_sales.csv'
    df.to_csv(output_path, index=False)
    print(f"\n✓ 创建示例数据文件: {output_path}")


def create_env_file():
    """创建 .env 文件"""
    env_file = Path(__file__).parent.parent / ".env"
    
    if not env_file.exists():
        env_example_file = Path(__file__).parent.parent / ".env.example"
        if env_example_file.exists():
            import shutil
            shutil.copy(env_example_file, env_file)
            print(f"\n✓ 从 .env.example 创建 .env 文件")
            print(f"  请编辑 .env 文件并填入正确的配置")
        else:
            print(f"\n✗ .env.example 文件不存在")
    else:
        print(f"\n✓ .env 文件已存在")


def main():
    """主函数"""
    print("=" * 60)
    print("Agent Skills 系统 - 初始化")
    print("=" * 60)
    print()
    
    # 1. 创建目录
    print("1. 创建必要的目录...")
    create_directories()
    
    # 2. 创建 .env 文件
    print("\n2. 检查配置文件...")
    create_env_file()
    
    # 3. 测试 Redis 连接
    print("\n3. 测试 Redis 连接...")
    redis_ok = test_redis_connection()
    
    # 4. 测试 LLM 连接
    print("\n4. 测试 LLM 连接...")
    llm_ok = test_llm_connection()
    
    # 5. 扫描技能
    print("\n5. 扫描技能...")
    skills_ok = scan_skills()
    
    # 6. 创建示例数据
    print("\n6. 创建示例数据...")
    create_sample_data()
    
    # 总结
    print()
    print("=" * 60)
    print("初始化完成!")
    print("=" * 60)
    
    print("\n状态:")
    print(f"  Redis:    {'✓ 正常' if redis_ok else '✗ 失败'}")
    print(f"  LLM:      {'✓ 正常' if llm_ok else '✗ 失败'}")
    print(f"  Skills:   {'✓ 正常' if skills_ok else '✗ 失败'}")
    
    if not redis_ok or not llm_ok:
        print("\n⚠️  部分组件连接失败,请检查配置并确保服务已启动")
        print("  Redis: docker-compose up -d redis")
        print("  Xinference: 参考 Xinference 文档启动服务")
    
    print("\n启动 API 服务:")
    print("  python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
    print()
    print("访问 API 文档: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
