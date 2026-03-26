# Agent Loop 架构重构说明

## 概述

本项目已完成对后端核心agent逻辑的Claude Code风格重构。新的架构基于"模型 + 工具 + 循环"的设计理念，提供了更清晰、模块化、可扩展的Agent Loop实现。

## 新架构特点

### 1. 核心设计理念
- **模型 + 工具 + 循环**: 所有复杂功能都基于这个简单而强大的架构
- **渐进式演进**: 支持从v0（单一工具）到v4（Skills机制）的演进路径
- **模块化设计**: 职责分离，易于维护和扩展

### 2. 新的组件结构

```
backend/core/agent_loop/
├── __init__.py              # 模块导出
├── agent_loop.py           # Agent Loop核心实现
├── agent_session.py        # Agent会话管理
├── context_manager.py      # 上下文管理
├── tool_registry.py        # 工具注册和管理
├── thought.py              # LLM思考和决策类
└── new_agent_runtime.py    # 新的Agent运行时（兼容原有API）
```

### 3. 核心组件说明

#### AgentLoop
- **职责**: 管理多个会话，执行单次循环
- **特点**: 
  - 支持会话状态持久化
  - 提供工具直接执行接口
  - 支持异步会话管理

#### AgentSession
- **职责**: 管理单个用户会话的完整生命周期
- **特点**:
  - 独立的对话历史管理
  - 支持TODO规划
  - 支持参数收集工作流

#### ContextManager
- **职责**: 管理对话上下文和工具执行历史
- **特点**:
  - Claude风格的上下文构建
  - 支持消息历史和工具结果管理
  - 最大消息数限制

#### ToolRegistry
- **职责**: 工具注册、管理和过滤
- **特点**:
  - 支持多种工具类别（文件、Shell、代码、技能等）
  - 按上下文智能过滤工具
  - 工具启用/禁用管理

#### Thought
- **职责**: 表示LLM思考和决策结果
- **特点**:
  - 支持多种动作类型（最终回答、工具使用、创建Todo、调度子代理等）
  - 统一的序列化/反序列化接口
  - 灵活的扩展机制

### 4. 新架构优势

#### a) 更好的模块化
- **解耦设计**: Agent Loop、会话管理、工具执行完全分离
- **单一职责**: 每个组件只做一件事
- **易于测试**: 组件可以独立测试

#### b) 更强的可扩展性
- **工具热插拔**: 无需修改核心代码即可添加新工具
- **插件化架构**: Skills可以按需加载和卸载
- **灵活的状态管理**: 支持多种会话状态和工作流

#### c) 更好的上下文管理
- **Claude风格上下文**: 更接近Claude Code的处理方式
- **增量式上下文**: 避免传递完整历史，减少token消耗
- **工具结果集成**: 工具执行结果自动集成到上下文中

#### d) 支持高级功能
- **TODO规划**: 支持显式任务规划和管理
- **子代理调度**: 支持创建专门处理子任务
- **参数收集**: 支持多轮参数收集工作流

## 兼容性说明

### 1. API兼容性
新的`NewAgentRuntime`类实现了与原`AgentRuntime`相同的接口：

#### 保持不变的接口:
```python
# 原有接口
async def chat(user_input, user_id, conversation_id=None, session_id=None) -> Dict

# 新的实现（兼容）
async def chat(user_input, user_id, conversation_id=None, session_id=None) -> Dict
```

#### 新增的接口:
```python
# 会话继续处理
async def continue_session(user_input, user_id, session_id=None, continuation_data=None)

# 获取会话状态
async def get_session_state(user_id, session_id=None)

# 清除会话
async def clear_session(user_id, session_id=None)

# 获取工具信息
def get_tools_info()
```

### 2. 响应格式兼容性
新的实现会将Agent Loop内部格式转换为原有的API响应格式，确保前端无需修改。

**转换示例**:
```python
# Agent Loop内部格式
{
    "success": True,
    "response": "处理结果...",
    "state": "completed",
    "session_id": "123",
    "user_id": "user_1",
    "mode": "direct"
}

# 转换为兼容格式（原有API期望的格式）
{
    "response": "处理结果...",
    "conversation_id": null,
    "session_id": "123",
    "mode": "direct",
    "state": "completed",
    "filled_slots": None,
    "next_slot": None,
    "ready_to_execute": True,
    "needs_confirmation": False,
    # ... 其他兼容字段
}
```

### 3. 技能执行兼容性
原有技能系统被包装为Agent Tools：

- 每个Skill变成一个`SkillExecutionTool`
- 原有的Skill执行逻辑保持不变
- 通过`execute_skill`方法提供向后兼容

## 迁移路径

### 阶段1: 并行运行（当前状态）
- 新的架构已经实现，但入口点仍然是原`AgentRuntime`
- 可以通过环境变量或配置开关选择使用新架构
- 原有API完全兼容

### 阶段2: 灰度迁移
1. **前端适配**: 更新前端以支持新的会话继续机制
2. **逐步切换**: 逐步将用户迁移到新的Agent Loop
3. **监控对比**: 对比新旧架构的性能和效果

### 阶段3: 完全切换
1. **移除旧代码**: 移除原有的`agent_runtime.py`
2. **重命名**: 将`new_agent_runtime.py`重命名为`agent_runtime.py`
3. **优化**: 根据使用情况优化Agent Loop配置

## 配置和定制

### 1. 系统提示定制
可以通过修改`AgentLoop`的`system_prompts`来定制助手的行为风格。

### 2. 工具配置
- **工具类别**: 可以定义新的工具类别
- **工具过滤**: 可以根据上下文智能过滤工具
- **工具权限**: 可以控制不同用户的工具访问权限

### 3. 性能调优
- **上下文长度**: 调整`ContextManager`的`max_messages`和`max_tool_results`
- **并发控制**: 调整Agent Loop的并发设置
- **缓存策略**: 优化会话状态缓存

## 测试和验证

### 1. 单元测试
```bash
# 运行Agent Loop测试
python test_agent_loop.py
```

### 2. 集成测试
- **对话流程测试**: 测试完整的对话工作流
- **技能执行测试**: 测试Skill到Tool的转换
- **会话状态测试**: 测试会话状态的保存和恢复

### 3. 性能测试
- **并发测试**: 多用户同时使用
- **长对话测试**: 测试上下文管理性能
- **工具延迟测试**: 测试工具执行性能

## 下一步工作

### 短期目标
1. **实现Todo管理器**: 参照`@s03_todo_write.py`实现显式规划
2. **实现子代理调度**: 参照`@s02_tool_use.py`实现子代理机制
3. **前端适配**: 更新前端以充分利用新功能

### 中期目标
1. **工具生态系统**: 构建丰富的工具库
2. **性能优化**: 优化Agent Loop性能
3. **监控和调试**: 添加详细的监控和调试工具

### 长期目标
1. **Skills体系**: 构建完整的Skills生态系统
2. **多模型支持**: 支持多种LLM模型的智能调度
3. **企业级特性**: 添加团队协作、审批流等企业级功能

## 故障排除

### 常见问题

#### Q1: 新架构不工作怎么办？
A: 检查是否所有依赖都已安装，确保LLM服务正常运行。

#### Q2: 工具执行失败怎么办？
A: 检查工具注册是否正确，参数是否符合定义。

#### Q3: 会话状态丢失怎么办？
A: 检查存储配置（如Redis）是否正常工作。

#### Q4: 响应格式不正确怎么办？
A: 检查格式转换逻辑，确保所有必需字段都已包含。

### 调试技巧
1. **启用详细日志**: 设置日志级别为DEBUG
2. **检查上下文**: 使用`get_session_state`查看完整的会话状态
3. **工具测试**: 使用`execute_tool_directly`测试单个工具
4. **简化测试**: 从简单的聊天开始，逐步增加复杂度

## 总结

新的Agent Loop架构为系统带来了以下核心价值：

1. **清晰的分层架构**: 职责明确，易于理解和维护
2. **强大的扩展性**: 支持从简单聊天到复杂工作流的演进
3. **卓越的兼容性**: 平滑迁移路径，最小化影响
4. **先进的功能**: 支持TODO规划、子代理等高级功能
5. **更好的用户体验**: 更智能的上下文管理，更自然的对话流程

通过逐步采用新架构，系统将能够更好地支持复杂的AI交互场景，并为未来的功能扩展奠定坚实基础。