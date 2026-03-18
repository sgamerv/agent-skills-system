"""基于LLM的Skill路由器"""
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from backend.llm.zhipuai_client import ZhipuAIClient
from backend.core.skill_manager import SkillRegistry

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """意图类型"""
    EXECUTE_SKILL = "execute_skill"
    VIEW_SKILLS = "view_skills"
    MODIFY_PARAMETERS = "modify_parameters"
    CONFIRM = "confirm"
    REJECT = "reject"
    HELP = "help"
    CHAT = "chat"


@dataclass
class Intent:
    """用户意图"""
    intent_type: IntentType
    target_skill: Optional[str] = None
    parameters: Dict[str, Any] = None
    confidence: float = 0.0
    reasoning: str = ""

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


@dataclass
class SkillMatch:
    """技能匹配结果"""
    skill_name: str
    relevance: float
    reasoning: str


@dataclass
class NextAction:
    """下一步动作"""
    action_type: str
    target: Optional[str] = None
    message: str = ""
    parameters: Dict[str, Any] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class IntentAnalyzer:
    """意图分析器"""

    SYSTEM_PROMPT = """你是一个智能助手，负责分析用户意图。根据用户的输入和对话历史，准确判断用户想要做什么。

请严格遵守以下规则：
1. 仔细分析用户输入的语义和上下文
2. 确定用户的真实意图
3. 提取相关的参数信息
4. 给出合理的置信度和理由

返回格式必须是有效的JSON。"""

    def __init__(self, llm_client: ZhipuAIClient):
        self.llm_client = llm_client

    async def analyze(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Intent:
        """
        分析用户意图

        Args:
            user_input: 用户输入
            context: 上下文（对话历史、会话状态等）

        Returns:
            Intent: 意图对象
        """
        prompt = self._build_intent_prompt(user_input, context)

        # 打印意图分析请求数据
        logger.info("=" * 80)
        logger.info("[IntentAnalyzer] 意图分析 - 请求数据")
        logger.info("=" * 80)
        logger.info(f"用户输入: {user_input}")
        logger.info(f"对话历史条数: {len(context.get('conversation_history', []))}")
        logger.info(f"会话状态: {context.get('session_state', {})}")
        logger.info(f"可用技能数: {len(context.get('available_skills', []))}")
        logger.info("-" * 80)
        logger.info("发送给LLM的Prompt:")
        logger.info(prompt)
        logger.info("-" * 80)

        try:
            # 准备输出示例，引导LLM返回正确的格式
            output_example = {
                "intent_type": "execute_skill",
                "target_skill": "data-analysis",
                "parameters": {"file_type": "csv"},
                "confidence": 0.95,
                "reasoning": "用户明确要求执行数据分析技能"
            }

            result = await self.llm_client.structured_output(
                messages=[{"role": "user", "content": prompt}],
                output_schema={
                    "type": "object",
                    "properties": {
                        "intent_type": {"type": "string"},
                        "target_skill": {"type": "string"},
                        "parameters": {"type": "object"},
                        "confidence": {"type": "number"},
                        "reasoning": {"type": "string"}
                    }
                },
                output_example=output_example
            )

            # 打印意图分析响应数据
            logger.info("[IntentAnalyzer] 意图分析 - 响应数据")
            logger.info("-" * 80)
            logger.info(f"LLM返回结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            logger.info(f"解析后的Intent:")
            logger.info(f"  - intent_type: {result.get('intent_type', 'chat')}")
            logger.info(f"  - target_skill: {result.get('target_skill')}")
            logger.info(f"  - parameters: {json.dumps(result.get('parameters', {}), ensure_ascii=False)}")
            logger.info(f"  - confidence: {result.get('confidence', 0.0)}")
            logger.info(f"  - reasoning: {result.get('reasoning', '')}")
            logger.info("=" * 80)

            return Intent(
                intent_type=IntentType(result.get("intent_type", "chat")),
                target_skill=result.get("target_skill"),
                parameters=result.get("parameters", {}),
                confidence=result.get("confidence", 0.0),
                reasoning=result.get("reasoning", "")
            )

        except Exception as e:
            logger.error(f"[IntentAnalyzer] 意图分析失败: {e}")
            # 返回默认聊天意图
            return Intent(
                intent_type=IntentType.CHAT,
                confidence=0.0,
                reasoning=f"意图分析失败: {str(e)}"
            )

    def _build_intent_prompt(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> str:
        """构建意图分析提示词"""
        prompt = f"""用户输入: {user_input}

"""

        # 添加对话历史
        if context.get("conversation_history"):
            prompt += "对话历史:\n"
            for msg in context["conversation_history"][-5:]:  # 最近5轮
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt += f"- {role}: {content}\n"
            prompt += "\n"

        # 添加当前会话状态
        if context.get("session_state"):
            prompt += f"当前会话状态: {json.dumps(context['session_state'], ensure_ascii=False)}\n\n"

        # 添加可用技能列表
        if context.get("available_skills"):
            prompt += "可用技能:\n"
            for skill in context["available_skills"]:
                prompt += f"- {skill['name']}: {skill.get('description', '')}\n"
            prompt += "\n"

        prompt += """请分析用户意图并返回JSON，包含以下字段：
- intent_type: 意图类型，可选值：
  * execute_skill: 执行技能
  * view_skills: 查看技能列表
  * modify_parameters: 修改参数
  * confirm: 确认操作
  * reject: 拒绝操作
  * help: 请求帮助
  * chat: 普通聊天
- target_skill: 目标技能名称（如果意图是执行技能）
- parameters: 提取的参数（字典格式）
- confidence: 置信度（0-1之间的浮点数）
- reasoning: 分析理由"""

        return prompt


class SkillMatcher:
    """技能匹配器"""

    SYSTEM_PROMPT = """你是一个智能助手，负责根据用户意图从可用技能中选择最匹配的技能。

请严格遵守以下规则：
1. 仔细分析用户意图和技能描述
2. 选择最相关的技能
3. 给出合理的匹配度评分和理由
4. 如果没有合适的技能，明确说明

返回格式必须是有效的JSON。"""

    def __init__(self, llm_client: ZhipuAIClient):
        self.llm_client = llm_client

    async def match(
        self,
        intent: Intent,
        available_skills: List[Dict[str, Any]]
    ) -> List[SkillMatch]:
        """
        匹配最合适的技能

        Args:
            intent: 用户意图
            available_skills: 可用技能列表

        Returns:
            List[SkillMatch]: 匹配结果，按相关度排序
        """
        if intent.intent_type != IntentType.EXECUTE_SKILL:
            return []

        prompt = self._build_match_prompt(intent, available_skills)

        # 打印技能匹配请求数据
        logger.info("=" * 80)
        logger.info("[SkillMatcher] 技能匹配 - 请求数据")
        logger.info("=" * 80)
        logger.info(f"用户意图: {intent.intent_type.value}")
        logger.info(f"目标技能: {intent.target_skill}")
        logger.info(f"提取参数: {json.dumps(intent.parameters, ensure_ascii=False)}")
        logger.info(f"置信度: {intent.confidence}")
        logger.info(f"分析理由: {intent.reasoning}")
        logger.info(f"可用技能数: {len(available_skills)}")
        logger.info("-" * 80)
        logger.info("可用技能列表:")
        for i, skill in enumerate(available_skills, 1):
            logger.info(f"  {i}. {skill['name']}")
            logger.info(f"     描述: {skill.get('description', '暂无描述')}")
            if skill.get('requires'):
                logger.info(f"     需要: {', '.join(skill['requires'])}")
            if skill.get('slots'):
                slot_desc = [f"{s['name']}{'(必填)' if s.get('required') else ''}" for s in skill['slots']]
                logger.info(f"     参数: {', '.join(slot_desc)}")
        logger.info("-" * 80)
        logger.info("发送给LLM的Prompt:")
        logger.info(prompt)
        logger.info("-" * 80)

        try:
            # 准备输出示例，引导LLM返回正确的格式
            output_example = {
                "matches": [
                    {
                        "skill_name": "data-analysis",
                        "relevance": 0.95,
                        "reasoning": "用户需要分析数据，该技能完全匹配"
                    }
                ],
                "need_more_info": True,
                "missing_parameters": ["file_path"]
            }

            result = await self.llm_client.structured_output(
                messages=[{"role": "user", "content": prompt}],
                output_schema={
                    "type": "object",
                    "properties": {
                        "matches": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "skill_name": {"type": "string"},
                                    "relevance": {"type": "number"},
                                    "reasoning": {"type": "string"}
                                }
                            }
                        },
                        "need_more_info": {"type": "boolean"},
                        "missing_parameters": {"type": "array", "items": {"type": "string"}}
                    }
                },
                output_example=output_example
            )

            # 打印技能匹配响应数据
            logger.info("[SkillMatcher] 技能匹配 - 响应数据")
            logger.info("-" * 80)
            logger.info(f"LLM返回结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            logger.info(f"需要更多信息: {result.get('need_more_info', False)}")
            logger.info(f"缺失参数: {result.get('missing_parameters', [])}")
            logger.info("匹配结果:")
            matches = []
            for match in result.get("matches", []):
                skill_match = SkillMatch(
                    skill_name=match["skill_name"],
                    relevance=match["relevance"],
                    reasoning=match["reasoning"]
                )
                matches.append(skill_match)
                logger.info(f"  - {skill_match.skill_name}")
                logger.info(f"    相关度: {skill_match.relevance}")
                logger.info(f"    理由: {skill_match.reasoning}")

            # 按相关度排序
            matches.sort(key=lambda x: x.relevance, reverse=True)
            logger.info(f"排序后结果: {[f'{m.skill_name}({m.relevance})' for m in matches]}")
            logger.info("=" * 80)

            return matches

        except Exception as e:
            logger.error(f"[SkillMatcher] 技能匹配失败: {e}")
            # 返回空匹配列表
            return []

    def _build_match_prompt(
        self,
        intent: Intent,
        available_skills: List[Dict[str, Any]]
    ) -> str:
        """构建技能匹配提示词"""
        prompt = f"""用户意图: {intent.intent_type.value}

"""

        if intent.target_skill:
            prompt += f"用户指定的技能: {intent.target_skill}\n"

        if intent.parameters:
            prompt += f"提取的参数: {json.dumps(intent.parameters, ensure_ascii=False)}\n"

        prompt += f"\n用户原始输入（用于上下文）: {intent.reasoning or '未提供'}\n\n"

        prompt += "可用技能列表:\n"
        for skill in available_skills:
            prompt += f"- {skill['name']}\n"
            prompt += f"  描述: {skill.get('description', '暂无描述')}\n"

            if skill.get('requires'):
                prompt += f"  需要: {', '.join(skill['requires'])}\n"

            if skill.get('slots'):
                prompt += f"  参数: "
                slot_desc = []
                for slot in skill['slots']:
                    slot_str = f"{slot['name']}"
                    if slot.get('required'):
                        slot_str += " (必填)"
                    slot_desc.append(slot_str)
                prompt += ', '.join(slot_desc) + "\n"

            prompt += "\n"

        prompt += """请选择最匹配的技能并返回JSON，包含以下字段：
- matches: 匹配的技能列表，每个包含：
  * skill_name: 技能名称
  * relevance: 相关度（0-1之间的浮点数）
  * reasoning: 匹配理由
- need_more_info: 是否需要更多信息（布尔值）
- missing_parameters: 缺少的参数列表

如果没有合适的技能，matches数组可以为空。"""

        return prompt


class WorkflowManager:
    """工作流管理器"""

    SYSTEM_PROMPT = """你是一个智能助手，负责管理多轮对话流程。

请严格遵守以下规则：
1. 理解当前对话状态和用户意图
2. 决定最合适的下一步动作
3. 给出清晰、友好的回复
4. 确保流程的连贯性和逻辑性

返回格式必须是有效的JSON。"""

    def __init__(self, llm_client: ZhipuAIClient):
        self.llm_client = llm_client

    async def decide_next_action(
        self,
        user_input: str,
        current_state: Dict[str, Any],
        context: Dict[str, Any]
    ) -> NextAction:
        """
        决定下一步动作

        Args:
            user_input: 用户输入
            current_state: 当前工作流状态
            context: 上下文

        Returns:
            NextAction: 下一步动作
        """
        prompt = self._build_decision_prompt(user_input, current_state, context)

        try:
            result = await self.llm_client.structured_output(
                messages=[{"role": "user", "content": prompt}],
                output_schema={
                    "type": "object",
                    "properties": {
                        "action_type": {"type": "string"},
                        "target": {"type": "string"},
                        "message": {"type": "string"},
                        "parameters": {"type": "object"}
                    }
                }
            )

            return NextAction(
                action_type=result.get("action_type", "chat"),
                target=result.get("target"),
                message=result.get("message", ""),
                parameters=result.get("parameters", {})
            )

        except Exception as e:
            logger.error(f"决策失败: {e}")
            # 返回默认聊天动作
            return NextAction(
                action_type="chat",
                message="抱歉，我遇到了一些问题。请重新描述您的需求。"
            )

    def _build_decision_prompt(
        self,
        user_input: str,
        current_state: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """构建决策提示词"""
        prompt = f"""当前状态: {current_state.get('state', 'unknown')}

用户最新输入: {user_input}

"""

        # 添加历史交互
        if context.get("conversation_history"):
            prompt += "历史交互:\n"
            for msg in context["conversation_history"][-5:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt += f"- {role}: {content}\n"
            prompt += "\n"

        # 添加已收集的参数
        if current_state.get("collected_parameters"):
            prompt += f"已收集参数: {json.dumps(current_state['collected_parameters'], ensure_ascii=False)}\n\n"

        # 添加当前技能信息
        if current_state.get("current_skill"):
            skill_name = current_state["current_skill"]
            skill_info = context.get("skill_info", {}).get(skill_name, {})
            prompt += f"当前技能: {skill_name}\n"
            if skill_info:
                prompt += f"技能描述: {skill_info.get('description', '')}\n"
                if skill_info.get('slots'):
                    prompt += f"需要的参数: {', '.join([s['name'] for s in skill_info['slots'] if s.get('required')])}\n"
            prompt += "\n"

        prompt += """可用的动作类型:
- execute_skill: 执行技能（所有参数已收集）
- collect_parameter: 收集参数（询问用户缺失的参数）
- confirm: 请求确认（所有参数收集完毕，需要用户确认）
- modify: 修改参数（用户想修改已收集的参数）
- complete: 完成任务
- chat: 普通聊天回复

请决定下一步动作并返回JSON，包含以下字段：
- action_type: 动作类型（上述值之一）
- target: 目标（技能名称或参数名）
- message: 要发送给用户的消息
- parameters: 相关参数（如果需要）"""

        return prompt


class LLMSkillRouter:
    """基于LLM的技能路由器"""

    def __init__(
        self,
        llm_client: ZhipuAIClient,
        skill_registry: SkillRegistry
    ):
        """
        初始化技能路由器

        Args:
            llm_client: LLM客户端
            skill_registry: 技能注册表
        """
        self.llm_client = llm_client
        self.skill_registry = skill_registry
        self.intent_analyzer = IntentAnalyzer(llm_client)
        self.skill_matcher = SkillMatcher(llm_client)
        self.workflow_manager = WorkflowManager(llm_client)

    async def route(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        路由用户请求到合适的技能

        Args:
            user_input: 用户输入
            context: 上下文信息

        Returns:
            Dict: 路由结果
        """
        # 打印路由请求数据
        logger.info("=" * 80)
        logger.info("[LLMSkillRouter] 路由请求")
        logger.info("=" * 80)
        logger.info(f"用户输入: {user_input}")
        logger.info(f"上下文: {json.dumps(context, ensure_ascii=False, indent=2)}")

        # 准备上下文
        context["available_skills"] = self._get_available_skills()

        # 1. 分析意图
        intent = await self.intent_analyzer.analyze(user_input, context)

        logger.info(f"[LLMSkillRouter] 意图分析结果: {intent.intent_type.value}, 置信度: {intent.confidence}")

        # 2. 根据意图类型处理
        if intent.intent_type == IntentType.VIEW_SKILLS:
            return self._handle_view_skills(context)

        elif intent.intent_type == IntentType.HELP:
            return self._handle_help()

        elif intent.intent_type == IntentType.EXECUTE_SKILL:
            # 3. 匹配技能
            matches = await self.skill_matcher.match(intent, context["available_skills"])

            if not matches:
                return {
                    "action": "no_match",
                    "message": "未找到匹配的技能，请重新描述您的需求或输入\"查看技能\"查看可用技能列表。"
                }

            best_match = matches[0]
            logger.info(f"最佳匹配: {best_match.skill_name}, 相关度: {best_match.relevance}")

            return {
                "action": "execute_skill",
                "skill_name": best_match.skill_name,
                "relevance": best_match.relevance,
                "reasoning": best_match.reasoning,
                "intent_parameters": intent.parameters,
                "alternatives": [
                    {"name": m.skill_name, "relevance": m.relevance}
                    for m in matches[1:4]
                ]
            }

        else:
            # 默认：普通聊天
            return {
                "action": "chat",
                "message": intent.reasoning or "请问您需要什么帮助？"
            }

    async def decide_next_action(
        self,
        user_input: str,
        current_state: Dict[str, Any],
        context: Dict[str, Any]
    ) -> NextAction:
        """
        决定下一步动作（用于多轮对话）

        Args:
            user_input: 用户输入
            current_state: 当前状态
            context: 上下文

        Returns:
            NextAction: 下一步动作
        """
        return await self.workflow_manager.decide_next_action(
            user_input,
            current_state,
            context
        )

    def _get_available_skills(self) -> List[Dict[str, Any]]:
        """获取可用技能列表"""
        skills = []
        for skill_name, metadata in self.skill_registry.skill_metadata.items():
            skill_info = {
                "name": skill_name,
                "description": metadata.get("description", ""),
                "requires": metadata.get("requires", []),
                "slots": metadata.get("slots", []),
                "workflow": metadata.get("workflow", {})
            }
            skills.append(skill_info)
        return skills

    def _handle_view_skills(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理查看技能请求"""
        skills = self._get_available_skills()

        message = "系统支持的技能列表：\n\n"
        for skill in skills:
            message += f"📌 **{skill['name']}**\n"
            message += f"   描述: {skill['description']}\n"

            if skill['slots']:
                required_slots = [s for s in skill['slots'] if s.get('required')]
                if required_slots:
                    message += f"   必需参数: {', '.join([s['name'] for s in required_slots])}\n"

            message += "\n"

        return {
            "action": "view_skills",
            "message": message,
            "skills": skills
        }

    def _handle_help(self) -> Dict[str, Any]:
        """处理帮助请求"""
        message = """欢迎使用智能助手系统！🎉

我可以帮您：
- 执行各种技能任务（数据分析、可视化、知识问答等）
- 查看可用的技能列表
- 提供操作帮助

使用方法：
1. 直接描述您的需求，我会自动匹配最合适的技能
2. 输入\"查看技能\"查看所有可用技能
3. 在执行过程中，根据提示提供所需信息
4. 随时输入\"取消\"可以中断当前操作

有什么我可以帮助您的吗？"""

        return {
            "action": "help",
            "message": message
        }
