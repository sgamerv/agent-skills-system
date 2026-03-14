"""对话管理器 - 管理多轮对话和 Slot Filling"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from config.prompts import CONFIRMATION_MESSAGE_TEMPLATE, SLOT_EXTRACTION_PROMPT
from models.dialogue import (
    DialogueContext,
    DialogueState,
    SlotDefinition,
    SlotValue,
)


logger = logging.getLogger(__name__)


class DialogueManager:
    """对话管理器 - 管理多轮对话和 Slot Filling"""

    def __init__(
        self,
        skill_registry: Any,
        skill_loader: Any,
        llm: Any,
        redis_client: Optional[Any] = None,
    ) -> None:
        self.skill_registry = skill_registry
        self.skill_loader = skill_loader
        self.llm = llm
        self.redis_client = redis_client
        self.active_dialogues: Dict[str, DialogueContext] = {}
    
    async def start_dialogue(
        self,
        skill_name: str,
        user_id: str,
        initial_input: str = None
    ) -> DialogueContext:
        """
        开始新的对话
        
        Args:
            skill_name: 目标 Skill 名称
            user_id: 用户 ID
            initial_input: 用户初始输入
        
        Returns:
            DialogueContext
        """
        # 1. 加载 Skill 定义
        slots_def = self._load_skill_slots(skill_name)
        
        # 2. 创建对话上下文
        conversation_id = self._generate_conversation_id()
        context = DialogueContext(
            conversation_id=conversation_id,
            user_id=user_id,
            skill_name=skill_name,
            state=DialogueState.INITIALIZING,
            slots_def=slots_def,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # 3. 初始化待填充槽位
        await self._initialize_slots(context)
        
        # 4. 保存对话上下文
        self.active_dialogues[conversation_id] = context
        if self.redis_client:
            await self._save_dialogue_to_redis(context)
        
        # 5. 如果有初始输入,尝试解析
        if initial_input:
            await self.process_user_input(conversation_id, initial_input)
        
        return context
    
    async def process_user_input(
        self,
        conversation_id: str,
        user_input: str
    ) -> Dict[str, Any]:
        """
        处理用户输入
        
        Returns:
            {
                "response": str,              # 响应消息
                "state": str,                 # 当前状态
                "filled_slots": dict,         # 已填充槽位
                "next_slot": str,            # 下一个需要填充的槽位
                "ready_to_execute": bool,      # 是否准备好执行
                "needs_confirmation": bool     # 是否需要确认
            }
        """
        context = self.active_dialogues.get(conversation_id)
        if not context:
            # 尝试从 Redis 加载
            if self.redis_client:
                context = await self._load_dialogue_from_redis(conversation_id)
            
            if not context:
                raise ValueError(f"Conversation {conversation_id} not found")
        
        # 添加用户消息到历史
        context.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # 1. 解析用户输入,提取槽位值
        extracted_slots = await self._extract_slots_from_input(
            context,
            user_input
        )
        
        # 2. 验证和填充槽位
        validation_result = await self._validate_and_fill_slots(
            context,
            extracted_slots
        )
        
        if not validation_result['success']:
            response = {
                "response": validation_result['error'],
                "state": context.state.value,
                "ready_to_execute": False
            }
            
            context.messages.append({
                "role": "assistant",
                "content": response['response'],
                "timestamp": datetime.now().isoformat()
            })
            
            context.updated_at = datetime.now().isoformat()
            if self.redis_client:
                await self._save_dialogue_to_redis(context)
            
            return response
        
        # 3. 检查是否所有必填槽位已填充
        if context.is_ready_for_execution():
            context.state = DialogueState.WAITING_CONFIRMATION
            # 生成确认消息
            confirmation = await self._generate_confirmation_message(context)
            
            response = {
                "response": confirmation,
                "state": context.state.value,
                "filled_slots": self._format_filled_slots(context),
                "ready_to_execute": True,
                "needs_confirmation": True
            }
            
            context.messages.append({
                "role": "assistant",
                "content": response['response'],
                "timestamp": datetime.now().isoformat()
            })
            
            context.updated_at = datetime.now().isoformat()
            if self.redis_client:
                await self._save_dialogue_to_redis(context)
            
            return response
        
        # 4. 获取下一个需要填充的槽位
        next_slot = context.get_next_slot_to_fill()
        if next_slot:
            context.state = DialogueState.SLOT_FILLING
            prompt = await self._generate_slot_prompt(context, next_slot)
            
            response = {
                "response": prompt,
                "state": context.state.value,
                "filled_slots": self._format_filled_slots(context),
                "next_slot": next_slot.name,
                "ready_to_execute": False,
                "needs_confirmation": False
            }
            
            context.messages.append({
                "role": "assistant",
                "content": response['response'],
                "timestamp": datetime.now().isoformat()
            })
            
            context.updated_at = datetime.now().isoformat()
            if self.redis_client:
                await self._save_dialogue_to_redis(context)
            
            return response
        
        # 5. 无法继续,返回错误
        error_msg = "抱歉,无法继续执行,请提供更多信息"
        context.messages.append({
            "role": "assistant",
            "content": error_msg,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "response": error_msg,
            "state": context.state.value,
            "ready_to_execute": False,
            "needs_confirmation": False
        }
    
    async def confirm_and_execute(
        self,
        conversation_id: str,
        confirmed: bool
    ) -> Dict[str, Any]:
        """确认并执行 Skill"""
        context = self.active_dialogues.get(conversation_id)
        if not context and self.redis_client:
            context = await self._load_dialogue_from_redis(conversation_id)
        
        if not context:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        if not confirmed:
            # 用户拒绝,询问要修改哪个槽位
            return await self._ask_for_modification(context)
        
        # 执行 Skill
        context.state = DialogueState.EXECUTING
        # result = await self._execute_skill(context)
        
        context.state = DialogueState.COMPLETED
        context.updated_at = datetime.now().isoformat()
        
        if self.redis_client:
            await self._save_dialogue_to_redis(context)
        
        # 模拟执行结果
        return {
            "response": f"已执行 {context.skill_name},完成所有操作",
            "state": context.state.value,
            "result": {"success": True}
        }
    
    def _load_skill_slots(self, skill_name: str) -> List[SlotDefinition]:
        """加载 Skill 的槽位定义"""
        slots_data = self.skill_loader.get_skill_slots(skill_name)
        
        return [
            SlotDefinition(
                name=slot['name'],
                type=slot['type'],
                required=slot['required'],
                description=slot['description'],
                prompt=slot['prompt'],
                options=slot.get('options'),
                validation=slot.get('validation'),
                default_value=slot.get('default_value'),
                depends_on=slot.get('depends_on')
            )
            for slot in slots_data
        ]
    
    async def _initialize_slots(self, context: DialogueContext):
        """初始化槽位,设置默认值"""
        for slot_def in context.slots_def:
            # 填充默认值
            if slot_def.default_value is not None:
                context.filled_slots[slot_def.name] = SlotValue(
                    name=slot_def.name,
                    value=slot_def.default_value,
                    source="default",
                    confidence=1.0,
                    timestamp=datetime.now().isoformat()
                )
            else:
                # 添加到待填充列表
                context.pending_slots.append(slot_def.name)
    
    async def _extract_slots_from_input(
        self,
        context: DialogueContext,
        user_input: str,
    ) -> Dict[str, Any]:
        """
        使用 LLM 从用户输入中提取槽位值

        Returns:
            {slot_name: extracted_value}
        """
        # 构建提示词
        slot_descriptions = []
        for slot_def in context.slots_def:
            desc = f"- {slot_def.name} ({slot_def.type}): {slot_def.description}"
            if slot_def.options:
                desc += f" 选项: {', '.join(slot_def.options.keys())}"
            slot_descriptions.append(desc)

        prompt = SLOT_EXTRACTION_PROMPT.format(
            slot_descriptions="\n".join(slot_descriptions),
            user_input=user_input,
        )

        try:
            response = await self.llm.ainvoke(prompt)
            # 尝试解析 JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse slot extraction response: %s", e)
        except Exception as e:
            logger.error("Error extracting slots: %s", e)

        return {}
    
    async def _validate_and_fill_slots(
        self,
        context: DialogueContext,
        extracted_slots: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证并填充槽位"""
        for slot_name, value in extracted_slots.items():
            slot_def = context._get_slot_def(slot_name)
            if not slot_def:
                continue
            
            # 验证槽位值
            validation = await self._validate_slot(slot_def, value, context)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': f"{slot_def.name} 无效: {validation['reason']}"
                }
            
            # 填充槽位
            context.filled_slots[slot_name] = SlotValue(
                name=slot_name,
                value=value,
                source="user",
                confidence=validation.get('confidence', 1.0),
                timestamp=datetime.now().isoformat()
            )
            
            # 从待填充列表中移除
            if slot_name in context.pending_slots:
                context.pending_slots.remove(slot_name)
        
        return {'success': True}
    
    async def _validate_slot(
        self,
        slot_def: SlotDefinition,
        value: Any,
        context: DialogueContext
    ) -> Dict[str, Any]:
        """验证单个槽位值"""
        # 类型验证
        if slot_def.type == 'enum':
            if value not in slot_def.options:
                return {
                    'valid': False,
                    'reason': f"必须是以下选项之一: {', '.join(slot_def.options.keys())}"
                }
        
        elif slot_def.type == 'file':
            import os
            # 文件扩展名验证
            if slot_def.validation and 'file_extension' in slot_def.validation:
                ext = os.path.splitext(str(value))[1].lower()
                if ext not in slot_def.validation['file_extension']:
                    return {
                        'valid': False,
                        'reason': f"文件扩展名必须是: {', '.join(slot_def.validation['file_extension'])}"
                    }
        
        # 自定义验证规则
        if slot_def.validation:
            # 可以添加更多验证逻辑
            pass
        
        return {'valid': True, 'confidence': 1.0}
    
    async def _generate_slot_prompt(
        self,
        context: DialogueContext,
        slot_def: SlotDefinition
    ) -> str:
        """生成槽位填充提示"""
        prompt = slot_def.prompt
        
        # 如果有选项,添加选项列表
        if slot_def.options:
            options_str = "\n".join([
                f"{key}: {value}"
                for key, value in slot_def.options.items()
            ])
            prompt = f"{prompt}\n\n选项:\n{options_str}"
        
        # 如果有依赖,提供上下文
        if slot_def.depends_on:
            context_info = []
            for dep_slot in slot_def.depends_on:
                if dep_slot in context.filled_slots:
                    context_info.append(f"{dep_slot}: {context.filled_slots[dep_slot].value}")
            
            if context_info:
                prompt += f"\n\n已确认: {', '.join(context_info)}"
        
        return prompt
    
    async def _generate_confirmation_message(self, context: DialogueContext) -> str:
        """生成确认消息"""
        filled_info = self._format_filled_slots(context)
        message = CONFIRMATION_MESSAGE_TEMPLATE.format(
            skill_name=context.skill_name,
            filled_info=filled_info
        )
        return message
    
    def _format_filled_slots(self, context: DialogueContext) -> str:
        """格式化已填充槽位"""
        lines = []
        for slot_name, slot_value in context.filled_slots.items():
            lines.append(f"- {slot_name}: {slot_value.value}")
        return "\n".join(lines)
    
    async def _ask_for_modification(self, context: DialogueContext) -> Dict[str, Any]:
        """询问用户要修改哪个槽位"""
        slots_list = "\n".join([
            f"- {name}: {slot.value.value}"
            for name, slot in context.filled_slots.items()
        ])
        
        message = f"请告诉我要修改哪个槽位:\n{slots_list}\n\n(直接输入槽位名和新的值)"
        
        return {
            "response": message,
            "state": DialogueState.SLOT_FILLING.value,
            "ready_to_execute": False,
            "needs_confirmation": False
        }
    
    def _generate_conversation_id(self) -> str:
        """生成对话 ID"""
        return str(uuid.uuid4())
    
    async def _save_dialogue_to_redis(self, context: DialogueContext):
        """保存对话上下文到 Redis"""
        if not self.redis_client:
            return
        
        key = f"dialogue:{context.conversation_id}"
        data = {
            "context": json.dumps(context.to_dict(), ensure_ascii=False),
            "updated_at": context.updated_at
        }
        await self.redis_client.hset(key, mapping=data)
        await self.redis_client.expire(key, 3600 * 24)  # 24小时过期
    
    async def _load_dialogue_from_redis(self, conversation_id: str) -> Optional[DialogueContext]:
        """从 Redis 加载对话上下文"""
        if not self.redis_client:
            return None
        
        key = f"dialogue:{conversation_id}"
        data = await self.redis_client.hgetall(key)
        
        if data:
            context_dict = json.loads(data.get('context', '{}'))
            context = DialogueContext.from_dict(context_dict)
            self.active_dialogues[conversation_id] = context
            return context
        return None
