"""技能管理器 - 负责技能的发现、加载和管理"""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


logger = logging.getLogger(__name__)


class SkillRegistry:
    """技能注册表 - 管理技能元数据"""

    def __init__(self, skills_dir: str) -> None:
        self.skills_dir = skills_dir
        self.skill_metadata: Dict[str, Dict[str, Any]] = {}
        self.scan_skills()
    
    def scan_skills(self) -> None:
        """扫描所有 Skills 并加载元数据"""
        if not os.path.exists(self.skills_dir):
            os.makedirs(self.skills_dir, exist_ok=True)
            return

        for skill_name in os.listdir(self.skills_dir):
            skill_path = os.path.join(self.skills_dir, skill_name)
            if not os.path.isdir(skill_path):
                continue

            skill_md = os.path.join(skill_path, "SKILL.md")
            if os.path.exists(skill_md):
                try:
                    metadata = self._extract_metadata(skill_md)
                    if metadata:
                        self.skill_metadata[skill_name] = metadata
                except Exception as e:
                    logger.warning("Failed to load skill %s: %s", skill_name, e)
    
    def _extract_metadata(self, skill_md_path: str) -> Optional[Dict[str, Any]]:
        """提取 SKILL.md 的 YAML frontmatter"""
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析 --- 之间的 YAML
        yaml_match = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
        if yaml_match:
            try:
                return yaml.safe_load(yaml_match.group(1))
            except yaml.YAMLError as e:
                print(f"Warning: Failed to parse YAML in {skill_md_path}: {e}")
        return None
    
    def get_skill_metadata(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """获取技能元数据"""
        return self.skill_metadata.get(skill_name)
    
    def list_skills(self) -> List[str]:
        """列出所有技能名称"""
        return list(self.skill_metadata.keys())
    
    def get_skills_summary(self) -> str:
        """获取技能摘要用于提示词"""
        summary_lines = []
        for name, metadata in self.skill_metadata.items():
            summary_lines.append(
                f"- {name}: {metadata.get('description', 'No description')}"
            )
        return "\n".join(summary_lines)
    
    def get_skill_dependencies(self, skill_name: str) -> List[str]:
        """获取技能依赖"""
        metadata = self.skill_metadata.get(skill_name, {})
        return metadata.get('requires', [])
    
    def get_skill_provides(self, skill_name: str) -> List[str]:
        """获取技能提供的输出"""
        metadata = self.skill_metadata.get(skill_name, {})
        return metadata.get('provides', [])
    
    def get_skill_can_call(self, skill_name: str) -> List[str]:
        """获取技能可以调用的其他技能"""
        metadata = self.skill_metadata.get(skill_name, {})
        return metadata.get('can_call', [])


class SkillLoader:
    """技能加载器 - 按需加载完整技能内容"""
    
    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir
    
    def load_skill(self, skill_name: str) -> Optional[str]:
        """加载完整的 SKILL.md 内容(去掉 YAML frontmatter)"""
        skill_path = os.path.join(self.skills_dir, skill_name, "SKILL.md")
        if not os.path.exists(skill_path):
            return None
        
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 去掉 YAML frontmatter,返回指令部分
        return re.sub(r'---\n.*?\n---', '', content, flags=re.DOTALL)
    
    def get_skill_slots(self, skill_name: str) -> List[Dict[str, Any]]:
        """获取技能的槽位定义"""
        skill_path = os.path.join(self.skills_dir, skill_name, "SKILL.md")
        if not os.path.exists(skill_path):
            return []
        
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析 YAML frontmatter
        yaml_match = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
        if yaml_match:
            try:
                metadata = yaml.safe_load(yaml_match.group(1))
                return metadata.get('slots', [])
            except yaml.YAMLError:
                pass
        
        return []


class ResourceManager:
    """资源管理器 - 管理技能的脚本和资源文件"""
    
    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir
    
    def get_script(self, skill_name: str, script_name: str) -> Optional[str]:
        """获取技能脚本内容"""
        script_path = os.path.join(self.skills_dir, skill_name, "scripts", script_name)
        if not os.path.exists(script_path):
            return None
        
        with open(script_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def execute_script(self, skill_name: str, script_name: str, **kwargs):
        """执行技能脚本"""
        import importlib.util
        
        script_path = os.path.join(self.skills_dir, skill_name, "scripts", script_name)
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        # 动态加载并执行
        spec = importlib.util.spec_from_file_location("skill_script", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 调用 execute 函数
        if hasattr(module, 'execute'):
            return module.execute(**kwargs)
        else:
            raise AttributeError(f"Script {script_name} does not have an 'execute' function")
    
    def get_asset(self, skill_name: str, asset_path: str) -> Optional[str]:
        """获取资源文件内容"""
        full_path = os.path.join(self.skills_dir, skill_name, "assets", asset_path)
        if not os.path.exists(full_path):
            return None
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def list_scripts(self, skill_name: str) -> List[str]:
        """列出技能的所有脚本"""
        scripts_dir = os.path.join(self.skills_dir, skill_name, "scripts")
        if not os.path.exists(scripts_dir):
            return []
        
        return [
            f for f in os.listdir(scripts_dir)
            if os.path.isfile(os.path.join(scripts_dir, f)) and f.endswith('.py')
        ]
