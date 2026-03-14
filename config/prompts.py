# 系统提示词模板

SYSTEM_PROMPT = '''你是一个智能助手,拥有以下技能:

{skills_info}

根据用户需求,选择合适的技能来完成任务。

在执行任务时:
1. 分析用户的真实意图
2. 识别需要的技能和参数
3. 如果缺少必要参数,通过多轮对话收集
4. 按依赖关系执行技能
5. 返回清晰、有用的结果

始终保持专业、友好的态度。
'''

INTENT_ANALYSIS_PROMPT = '''分析用户意图,确定需要的 Skill:

用户输入: {user_input}

可用 Skills:
{skills_summary}

以 JSON 格式返回:
{
  "skill": "skill_name",
  "needs_slot_filling": true/false,
  "extracted_params": {...},
  "confidence": 0.95
}

注意: 如果用户输入缺少必要的参数,needs_slot_filling 应该为 true
'''

SLOT_EXTRACTION_PROMPT = '''分析用户输入,提取以下槽位的值:

槽位定义:
{slot_descriptions}

用户输入: {user_input}

以 JSON 格式返回提取的槽位值:
{
  "slot_name": value,
  ...
}

如果无法提取某个槽位的值,不要包含该槽位。
'''

CONFIRMATION_MESSAGE_TEMPLATE = '''即将执行 {skill_name},确认以下信息:

{filled_info}

确认执行吗?(是/否)
'''

SKILL_EXECUTION_PROMPT = '''你正在执行 {skill_name} 技能。

技能描述: {description}

执行步骤:
{steps}

当前参数:
{parameters}

执行任务并返回结果。
'''

MEMORY_INJECTION_PROMPT = '''以下是相关的对话记忆和用户画像信息:

对话记忆:
{dialogue_memory}

用户画像:
{user_profile}

利用这些信息来更好地理解用户需求并提供个性化服务。
'''

# RAG 相关提示词

RAG_CONTEXT_PROMPT = '''基于以下上下文回答问题:

上下文:
{context}

问题: {query}

回答:'''

RAG_SYSTEM_PROMPT = '''你是一个专业的知识问答助手。
基于提供的文档内容回答用户问题。
如果上下文中没有相关信息,明确告知用户。
回答要准确、简洁、有依据。
'''
