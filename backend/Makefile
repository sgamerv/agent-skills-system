# Agent Skills System - Makefile
# 提供常用开发命令的快捷方式

.PHONY: help install install-dev test lint format check clean run serve

# 默认目标
help:
	@echo "Agent Skills System - 开发命令"
	@echo ""
	@echo "可用命令:"
	@echo "  make install       - 安装基础依赖"
	@echo "  make install-dev   - 安装开发依赖"
	@echo "  make format        - 格式化代码"
	@echo "  make lint          - 检查代码风格"
	@echo "  make type-check    - 类型检查"
	@echo "  make check         - 运行所有检查"
	@echo "  make test          - 运行测试"
	@echo "  make test-cov      - 运行测试并生成覆盖率报告"
	@echo "  make clean         - 清理临时文件"
	@echo "  make init-db       - 初始化数据库"
	@echo "  make serve         - 启动 API 服务"
	@echo "  make docker-up     - 启动 Docker 服务"
	@echo "  make docker-down   - 停止 Docker 服务"

# 安装依赖
install:
	@echo "安装基础依赖..."
	pip install -e .

install-dev:
	@echo "安装开发依赖..."
	pip install -e .[dev]

# 代码格式化
format:
	@echo "格式化代码..."
	black .
	ruff check --fix .

# 代码检查
lint:
	@echo "检查代码风格..."
	ruff check .
	black --check .

# 类型检查
type-check:
	@echo "运行类型检查..."
	mypy .

# 运行所有检查
check:
	@echo "运行所有检查..."
	python scripts/check_code_style.py

# 运行测试
test:
	@echo "运行测试..."
	pytest tests/ -v

test-cov:
	@echo "运行测试并生成覆盖率报告..."
	pytest tests/ -v --cov=api --cov=core --cov=models --cov-report=html

# 清理临时文件
clean:
	@echo "清理临时文件..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	find . -type f -name '*.pyo' -delete 2>/dev/null || true
	find . -type f -name '.DS_Store' -delete 2>/dev/null || true
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache/ .ruff_cache/ htmlcov/ .coverage 2>/dev/null || true

# 初始化数据库
init-db:
	@echo "初始化数据库..."
	python scripts/init_db.py

# 启动 API 服务
serve:
	@echo "启动 API 服务..."
	python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Docker 操作
docker-up:
	@echo "启动 Docker 服务..."
	docker-compose up -d

docker-down:
	@echo "停止 Docker 服务..."
	docker-compose down

docker-logs:
	docker-compose logs -f
