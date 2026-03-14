#!/usr/bin/env python3
"""代码规范检查脚本 - 检查项目是否符合 Python 3.10+ 开发规范"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """
    运行命令并返回是否成功

    Args:
        cmd: 命令列表
        description: 命令描述

    Returns:
        是否成功
    """
    print(f"\n{'=' * 60}")
    print(f"运行: {description}")
    print(f"命令: {' '.join(cmd)}")
    print(f"{'=' * 60}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        print(f"❌ {description} 失败 (退出码: {result.returncode})")
        return False

    print(f"✅ {description} 成功")
    return True


def check_python_version() -> bool:
    """检查 Python 版本"""
    print("\n" + "=" * 60)
    print("检查 Python 版本")
    print("=" * 60)

    version = sys.version_info
    print(f"当前 Python 版本: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 12):
        print("❌ Python 版本必须 >= 3.12")
        return False

    print("✅ Python 版本符合要求")
    return True


def check_imports() -> bool:
    """检查导入顺序和风格"""
    print("\n" + "=" * 60)
    print("检查导入风格 (使用 ruff)")
    print("=" * 60)

    return run_command(
        ["ruff", "check", "--select=I", "."],
        "导入顺序检查",
    )


def check_code_format() -> bool:
    """检查代码格式"""
    print("\n" + "=" * 60)
    print("检查代码格式 (使用 black --check)")
    print("=" * 60)

    return run_command(
        ["black", "--check", "."],
        "代码格式检查",
    )


def check_code_quality() -> bool:
    """检查代码质量"""
    print("\n" + "=" * 60)
    print("检查代码质量 (使用 ruff)")
    print("=" * 60)

    return run_command(
        ["ruff", "check", "."],
        "代码质量检查",
    )


def check_type_hints() -> bool:
    """检查类型注解"""
    print("\n" + "=" * 60)
    print("检查类型注解 (使用 mypy)")
    print("=" * 60)

    return run_command(
        ["mypy", "."],
        "类型注解检查",
    )


def check_security() -> bool:
    """检查安全问题"""
    print("\n" + "=" * 60)
    print("检查安全问题 (使用 bandit)")
    print("=" * 60)

    # bandit 可能未安装,跳过不影响结果
    result = subprocess.run(
        ["bandit", "-r", ".", "-c", "pyproject.toml"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 127:  # command not found
        print("⚠️  bandit 未安装,跳过安全检查")
        print("   安装方法: pip install bandit")
        return True

    if result.stdout:
        print(result.stdout)

    if result.stderr and "Error:" in result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        print("⚠️  发现安全问题")
        return False

    print("✅ 安全检查通过")
    return True


def run_tests() -> bool:
    """运行测试"""
    print("\n" + "=" * 60)
    print("运行测试 (使用 pytest)")
    print("=" * 60)

    # 测试可能不存在,跳过不影响结果
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("⚠️  测试目录不存在,跳过测试")
        return True

    return run_command(
        ["pytest", "tests/", "-v", "--tb=short"],
        "测试运行",
    )


def main() -> int:
    """主函数"""
    print("=" * 60)
    print("Agent Skills System - 代码规范检查")
    print("=" * 60)

    # 检查 Python 版本
    if not check_python_version():
        return 1

    results = []

    # 检查导入
    results.append(check_imports())

    # 检查代码格式
    results.append(check_code_format())

    # 检查代码质量
    results.append(check_code_quality())

    # 检查类型注解
    results.append(check_type_hints())

    # 检查安全问题
    results.append(check_security())

    # 运行测试
    results.append(run_tests())

    # 总结
    print("\n" + "=" * 60)
    print("检查总结")
    print("=" * 60)

    total = len(results)
    passed = sum(results)
    failed = total - passed

    print(f"总检查项: {total}")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")

    if failed > 0:
        print("\n❌ 有检查项失败,请修复后重试")
        print("\n常用修复命令:")
        print("  # 自动修复代码风格问题")
        print("  ruff check --fix .")
        print("  # 自动格式化代码")
        print("  black .")
        print("  # 安装缺失的工具")
        print("  pip install -e .[dev]")
        return 1

    print("\n✅ 所有检查通过!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
