"""FastAPI 应用主入口"""
from __future__ import annotations

import asyncio
import uvicorn
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import settings
from backend.config.logging_config import get_logger, setup_logging
from backend.core.memory import ProfileManager
from backend.core.session_manager import MessageManager, SessionManager
from backend.core.llm_provider_factory import LLMProviderFactory

# 配置全局日志
setup_logging(level=settings.LOG_LEVEL_INT)

logger = get_logger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Agent Skills 知识问答+任务处理系统",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局依赖
@app.on_event("startup")
async def startup_event() -> None:
    """应用启动事件"""
    import redis.asyncio as redis

    # 测试LLM连接
    logger.info(f"测试LLM连接，提供者: {settings.LLM_PROVIDER}")
    llm_connection_ok = LLMProviderFactory.test_connection()
    if not llm_connection_ok:
        logger.error("LLM连接测试失败！请检查配置")
    else:
        logger.info("LLM连接测试成功")

    # 初始化 Redis 客户端
    redis_client = None
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        # 只尝试创建客户端，不检查ping以避免异步问题
        logger.info("Redis客户端已创建")
    except Exception as e:
        logger.warning("Failed to create Redis client: %s", e)
        redis_client = None

    # 初始化核心组件
    # 根据配置选择Agent运行时架构
    if settings.AGENT_ARCHITECTURE.lower() == "agent_loop":
        from backend.core.agent_loop.new_agent_runtime import NewAgentRuntime
        app.state.agent = NewAgentRuntime(redis_client=redis_client)
        logger.info(f"使用新的Agent Loop架构: {settings.AGENT_ARCHITECTURE}")
    else:
        from backend.core.agent_runtime import AgentRuntime
        app.state.agent = AgentRuntime(redis_client=redis_client)
        logger.info(f"使用传统架构: {settings.AGENT_ARCHITECTURE}")
    
    app.state.session_manager = SessionManager(redis_client=redis_client)
    app.state.message_manager = MessageManager(redis_client=redis_client)
    app.state.profile_manager = ProfileManager(redis_client=redis_client)

    logger.info("%s started successfully!", settings.APP_NAME)


# API 模型

class ChatRequest(BaseModel):
    """聊天请求"""
    user_input: str
    user_id: str
    conversation_id: Optional[str] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str
    conversation_id: Optional[str] = None
    session_id: Optional[str] = None
    mode: str
    state: str
    filled_slots: Optional[Dict[str, Any]] = None
    next_slot: Optional[str] = None
    ready_to_execute: bool = False
    needs_confirmation: bool = False
    # 新增字段
    available_skills: Optional[List[Dict[str, Any]]] = None
    current_slot: Optional[Dict[str, Any]] = None
    collected_parameters: Optional[Dict[str, Any]] = None
    execution_result: Optional[Dict[str, Any]] = None
    task_id: Optional[str] = None
    feedback_required: bool = False
    feedback: Optional[Dict[str, Any]] = None
    next_action: Optional[str] = None


class ExecuteSkillRequest(BaseModel):
    """执行技能请求"""
    skill_name: str
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class SkillListResponse(BaseModel):
    """技能列表响应"""
    skills: List[Dict[str, Any]]
    total: int


class SessionCreateRequest(BaseModel):
    """创建会话请求"""
    user_id: str
    title: Optional[str] = None


class SessionResponse(BaseModel):
    """会话响应"""
    session_id: str
    user_id: str
    status: str
    title: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class SessionUpdateRequest(BaseModel):
    """更新会话请求"""
    title: str


# API 路由

@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    agent = app.state.agent

    # 通用健康检查字段
    health_data = {
        "status": "healthy",
        "llm_provider": settings.LLM_PROVIDER,
        "llm_available": agent.llm is not None if hasattr(agent, 'llm') else False,
        "agent_architecture": settings.AGENT_ARCHITECTURE,
    }
    
    # 传统架构特有字段
    if hasattr(agent, 'zhipuai_client'):
        health_data["zhipuai_available"] = agent.zhipuai_client is not None
    
    if hasattr(agent, 'workflow_executor'):
        health_data["workflow_executor_available"] = agent.workflow_executor is not None
    
    # Agent Loop架构特有字段
    if hasattr(agent, 'agent_loop'):
        health_data["agent_loop_available"] = True
        if hasattr(agent, 'tool_registry'):
            health_data["tool_count"] = str(len(agent.tool_registry.get_all_tools()))  # 转换为字符串
    
    return health_data


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    聊天接口

    支持多轮对话和 Slot Filling
    """
    agent = app.state.agent

    # 记录请求信息
    logger.info(f"收到聊天请求: user_id={request.user_id}, session_id={request.session_id}, user_input={request.user_input[:50]}")

    # 检查LLM是否可用
    if agent.llm is None:
        logger.error("LLM客户端不可用，无法处理请求")
        raise HTTPException(
            status_code=503,
            detail="无法连接到LLM服务，请检查配置或稍后重试"
        )

    try:
        result = await agent.chat(
            user_input=request.user_input,
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            session_id=request.session_id,
        )

        # 确保所有必需字段都有值
        return ChatResponse(
            response=result.get("response", ""),
            conversation_id=result.get("conversation_id"),
            session_id=result.get("session_id"),
            mode=result.get("mode", "direct"),
            state=result.get("state", "completed"),
            filled_slots=result.get("filled_slots"),
            next_slot=result.get("next_slot"),
            ready_to_execute=result.get("ready_to_execute", False),
            needs_confirmation=result.get("needs_confirmation", False),
            available_skills=result.get("available_skills"),
            current_slot=result.get("current_slot"),
            collected_parameters=result.get("collected_parameters"),
            execution_result=result.get("execution_result"),
            task_id=result.get("task_id"),
            feedback_required=result.get("feedback_required", False),
            feedback=result.get("feedback"),
            next_action=result.get("next_action")
        )
    except Exception as e:
        logger.error("Chat error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/execute-skill")
async def execute_skill(request: ExecuteSkillRequest) -> Dict[str, Any]:
    """
    直接执行技能

    不需要经过对话流程,直接执行指定技能
    """
    agent = app.state.agent

    try:
        result = await agent.execute_skill(
            skill_name=request.skill_name,
            parameters=request.parameters,
            context=request.context,
        )
        return {
            "skill": request.skill_name,
            "success": result.success,
            "output": result.output,
            "error": result.error,
        }
    except Exception as e:
        logger.error("Skill execution error: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/skills", response_model=SkillListResponse)
async def list_skills():
    """
    获取所有可用技能列表
    """
    agent = app.state.agent
    
    skills = []
    for skill_name, metadata in agent.skill_registry.skill_metadata.items():
        skills.append({
            "name": skill_name,
            "description": metadata.get('description', ''),
            "category": metadata.get('category', ''),
            "tags": metadata.get('tags', []),
            "version": metadata.get('version', '1.0.0')
        })
    
    return SkillListResponse(
        skills=skills,
        total=len(skills)
    )


@app.get("/skills/{skill_name}")
async def get_skill(skill_name: str):
    """
    获取指定技能的详细信息
    """
    agent = app.state.agent
    
    metadata = agent.skill_registry.get_skill_metadata(skill_name)
    if not metadata:
        raise HTTPException(status_code=404, detail=f"Skill {skill_name} not found")
    
    # 获取槽位定义
    slots = agent.skill_loader.get_skill_slots(skill_name)
    
    return {
        **metadata,
        "slots": slots,
        "can_call": agent.skill_registry.get_skill_can_call(skill_name)
    }


@app.post("/sessions", response_model=SessionResponse)
async def create_session(request: SessionCreateRequest):
    """
    创建新会话
    """
    session_manager: SessionManager = app.state.session_manager
    
    try:
        session = await session_manager.create_session(
            user_id=request.user_id,
            title=request.title
        )
        return SessionResponse(**session.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """
    获取会话信息
    """
    session_manager: SessionManager = app.state.session_manager
    
    session = await session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    return SessionResponse(**session.to_dict())


@app.get("/users/{user_id}/sessions")
async def get_user_sessions(user_id: str):
    """
    获取用户的所有会话
    """
    session_manager: SessionManager = app.state.session_manager
    
    try:
        sessions = await session_manager.get_user_sessions(user_id)
        return {
            "sessions": [s.to_dict() for s in sessions],
            "total": len(sessions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/sessions/{session_id}", response_model=SessionResponse)
async def update_session(session_id: str, request: SessionUpdateRequest):
    """
    更新会话标题
    """
    session_manager: SessionManager = app.state.session_manager

    session = await session_manager.update_session(session_id, title=request.title)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    return SessionResponse(**session.to_dict())


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    删除会话及其所有消息
    """
    session_manager: SessionManager = app.state.session_manager

    success = await session_manager.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete session")

    return {"message": "Session deleted successfully"}


@app.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, limit: int = 50):
    """
    获取会话的所有消息
    """
    message_manager: MessageManager = app.state.message_manager
    
    try:
        messages = await message_manager.get_session_messages(session_id, limit)
        return {
            "messages": [m.to_dict() for m in messages],
            "total": len(messages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users/{user_id}/profile")
async def get_user_profile(user_id: str):
    """
    获取用户画像
    """
    profile_manager: ProfileManager = app.state.profile_manager
    
    try:
        profile = await profile_manager.get_profile(user_id)
        return profile.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users/{user_id}/memories")
async def get_user_memories(user_id: str, memory_type: Optional[str] = None, limit: int = 10):
    """
    获取用户的记忆
    """
    from backend.models.memory import MemoryType
    
    agent = app.state.agent
    
    try:
        mem_type = MemoryType(memory_type) if memory_type else None
        memories = await agent.memory_manager.get_memories(user_id, mem_type, limit)
        return {
            "memories": [m.to_dict() for m in memories],
            "total": len(memories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
