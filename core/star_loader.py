"""
EgoPitch Core Module - 星球配置加载器
实现"球星即Skill"的可插拔设计
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("EgoPitch.StarLoader")

CONFIGS_DIR = Path("configs/stars")


@dataclass
class TriggerCategory:
    """触发词分类"""
    words: List[str]
    score: int
    description: str


@dataclass
class LayerConfig:
    """人格层级配置"""
    name: str
    name_en: str
    activation: str
    tone: str
    style: str
    traits: List[str]
    example_responses: List[str]
    system_prompt: str


@dataclass
class StarConfig:
    """球星完整配置"""
    id: str
    name: str
    full_name: str
    description: str
    avatar: str
    trigger_words: Dict[str, TriggerCategory]
    pain_points: List[str]
    layers: Dict[int, LayerConfig]
    achievements: List[str]
    explosive_quotes: List[str]

    def get_layer_prompt(self, layer: int, anger: int) -> str:
        """生成指定层级的人格提示"""
        layer_config = self.layers.get(layer)
        if not layer_config:
            logger.warning(f"层级 {layer} 不存在，使用默认")
            layer_config = self.layers[1]

        prompt = f"{layer_config.system_prompt}\n当前怒气值：{anger}%"

        # 核爆模式特殊处理：添加爆炸性内容
        if layer == 3:
            # 随机选择一个爆炸性言论作为参考
            import random
            quote_hint = random.choice(self.explosive_quotes)
            prompt += f"\n\n参考表达风格：'{quote_hint}'"

        return prompt

    def calculate_trigger_anger(self, message: str) -> int:
        """根据触发词计算怒气增加值"""
        anger = 0
        triggered = []

        for category_name, category in self.trigger_words.items():
            for word in category.words:
                if word in message:
                    anger += category.score
                    triggered.append(f"{category_name}:{word}(+{category.score})")

        if triggered:
            logger.info(f"[{self.name}] 触发词检测: {triggered}")

        return anger


class StarLoader:
    """球星配置加载器"""

    _stars: Dict[str, StarConfig] = {}
    _loaded = False

    @classmethod
    def load_all(cls) -> Dict[str, StarConfig]:
        """加载所有球星配置"""
        if cls._loaded:
            return cls._stars

        configs_path = CONFIGS_DIR
        if not configs_path.exists():
            logger.warning(f"配置目录不存在: {configs_path}")
            return cls._stars

        for config_file in configs_path.glob("*.json"):
            try:
                star = cls._parse_config(config_file)
                cls._stars[star.id] = star
                logger.info(f"加载球星配置: {star.name} ({star.id})")
            except Exception as e:
                logger.error(f"加载配置失败 {config_file}: {e}")

        cls._loaded = True
        return cls._stars

    @classmethod
    def get_star(cls, star_id: str) -> Optional[StarConfig]:
        """获取指定球星配置"""
        if not cls._loaded:
            cls.load_all()
        return cls._stars.get(star_id)

    @classmethod
    def get_all_stars(cls) -> List[StarConfig]:
        """获取所有球星列表"""
        if not cls._loaded:
            cls.load_all()
        return list(cls._stars.values())

    @classmethod
    def _parse_config(cls, config_file: Path) -> StarConfig:
        """解析JSON配置文件"""
        with open(config_file, encoding="utf-8") as f:
            data = json.load(f)

        # 解析触发词分类
        trigger_words = {}
        for category_name, cat_data in data.get("trigger_words", {}).items():
            trigger_words[category_name] = TriggerCategory(
                words=cat_data["words"],
                score=cat_data["score"],
                description=cat_data["description"]
            )

        # 解析层级配置
        layers = {}
        for layer_num, layer_data in data.get("layers", {}).items():
            behavior = layer_data.get("behavior", {})
            layers[int(layer_num)] = LayerConfig(
                name=layer_data["name"],
                name_en=layer_data["name_en"],
                activation=layer_data["activation"],
                tone=behavior.get("tone", ""),
                style=behavior.get("style", ""),
                traits=behavior.get("traits", []),
                example_responses=behavior.get("example_responses", []),
                system_prompt=layer_data.get("system_prompt", "")
            )

        return StarConfig(
            id=data["id"],
            name=data["name"],
            full_name=data["full_name"],
            description=data["description"],
            avatar=data.get("avatar", ""),
            trigger_words=trigger_words,
            pain_points=data.get("pain_points", []),
            layers=layers,
            achievements=data.get("achievements", []),
            explosive_quotes=data.get("explosive_quotes", [])
        )