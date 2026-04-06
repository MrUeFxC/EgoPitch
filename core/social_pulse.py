"""
EgoPitch Core Module - 社交媒体舆论注入系统
模拟 X/TikTok 评论流作为外部刺激
"""

import json
import random
import logging
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from openai import OpenAI

logger = logging.getLogger("EgoPitch.SocialPulse")

CONFIG_FILE = Path("configs/social_media.json")


@dataclass
class Comment:
    """一条社交媒体评论"""
    content: str
    type: str
    sentiment: str
    weight: int
    likes: int


class SocialPulse:
    """社交媒体舆论注入系统"""

    def __init__(self, client: OpenAI, model: str = "qwen-plus"):
        self.client = client
        self.model = model
        self.config = self._load_config()
        self.comment_history: List[Comment] = []
        self.current_sentiment = 0  # 当前负面舆论累计值

    def _load_config(self) -> Dict:
        """加载舆论配置"""
        if not CONFIG_FILE.exists():
            logger.warning(f"舆论配置文件不存在: {CONFIG_FILE}")
            return {"comment_types": {}, "pulse_settings": {}}

        with open(CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)

    def generate_comments(
        self,
        topic: Optional[str] = None,
        count: int = 3,
        star_name: str = "C罗"
    ) -> List[Comment]:
        """
        生成一批模拟评论

        Args:
            topic: 话题关键词，影响评论倾向
            count: 生成数量
            star_name: 星名称，用于@提及
        """
        comments = []
        comment_types = self.config.get("comment_types", {})

        # 确定评论类型分布
        if topic:
            # 根据话题倾向调整分布
            bias = self._get_topic_bias(topic)
            type_weights = self._get_biased_weights(bias)
        else:
            # 默认分布：更多负面评论
            type_weights = {
                "fan": 0.2,
                "hater": 0.4,
                "neutral": 0.25,
                "provocative": 0.15
            }

        # 生成评论
        for _ in range(count):
            type_name = self._weighted_choice(type_weights)
            type_config = comment_types.get(type_name, {})

            templates = type_config.get("templates", [])
            if not templates:
                continue

            # 选择模板并可能用AI增强
            base_content = random.choice(templates)

            # 添加@提及
            if self.config.get("pulse_settings", {}).get("enable_at_mentions", True):
                if type_name in ["hater", "provocative"]:
                    base_content = f"@{star_name} {base_content}"

            comment = Comment(
                content=base_content,
                type=type_name,
                sentiment=type_config.get("sentiment", "neutral"),
                weight=type_config.get("weight", 0),
                likes=random.randint(100, 5000)
            )
            comments.append(comment)

        self.comment_history.extend(comments)
        self._update_sentiment(comments)

        logger.info(f"生成 {len(comments)} 条评论，累计负面舆论: {self.current_sentiment}")
        return comments

    def generate_ai_comment(
        self,
        context: str,
        star_name: str = "C罗",
        sentiment: str = "negative"
    ) -> Comment:
        """用AI生成更真实的评论"""
        try:
            sentiment_prompt = {
                "positive": "你是球星的铁粉，表达无条件支持和爱",
                "neutral": "你是理性的球迷，客观分析，不带情绪",
                "negative": "你是黑粉或质疑者，批评球星的表现或行为"
            }

            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=80,
                messages=[
                    {
                        "role": "system",
                        "content": f"{sentiment_prompt.get(sentiment, 'neutral')}\n"
                        f"用简短的社交媒体评论风格回复（不超过30字）。\n"
                        f"可以@{star_name} 提及球星。"
                    },
                    {"role": "user", "content": f"针对这个话题发一条评论: {context}"}
                ],
            )

            content = response.choices[0].message.content.strip()
            weight = {"positive": -3, "neutral": 2, "negative": 8}.get(sentiment, 0)

            comment = Comment(
                content=content,
                type="ai_generated",
                sentiment=sentiment,
                weight=weight,
                likes=random.randint(50, 2000)
            )

            self.comment_history.append(comment)
            self.current_sentiment += weight
            logger.info(f"AI生成评论: '{content}' (weight={weight})")

            return comment

        except Exception as e:
            logger.error(f"AI生成评论失败: {e}")
            return Comment("", "error", "neutral", 0, 0)

    def get_sentiment_value(self) -> int:
        """获取当前负面舆论累计值"""
        return self.current_sentiment

    def reset_sentiment(self):
        """重置舆论累计值"""
        self.current_sentiment = 0
        self.comment_history = []

    def _get_topic_bias(self, topic: str) -> str:
        """根据话题确定评论倾向"""
        hot_topics = self.config.get("hot_topics", [])
        for ht in hot_topics:
            if any(kw in topic for kw in ht.get("keywords", [])):
                return ht.get("comment_bias", "hater")
        return "hater"

    def _get_biased_weights(self, bias: str) -> Dict[str, float]:
        """根据倾向调整评论类型权重"""
        base_weights = {
            "fan": 0.15,
            "hater": 0.35,
            "neutral": 0.25,
            "provocative": 0.25
        }

        if bias == "provocative":
            base_weights["provocative"] = 0.45
            base_weights["hater"] = 0.35
            base_weights["fan"] = 0.1
        elif bias == "hater":
            base_weights["hater"] = 0.5
            base_weights["fan"] = 0.1

        return base_weights

    def _weighted_choice(self, weights: Dict[str, float]) -> str:
        """加权随机选择"""
        total = sum(weights.values())
        r = random.uniform(0, total)

        cumulative = 0
        for choice, weight in weights.items():
            cumulative += weight
            if r <= cumulative:
                return choice

        return list(weights.keys())[0]

    def _update_sentiment(self, comments: List[Comment]):
        """更新舆论累计值"""
        for comment in comments:
            if comment.sentiment == "negative":
                self.current_sentiment += comment.weight
            elif comment.sentiment == "positive":
                self.current_sentiment -= abs(comment.weight)