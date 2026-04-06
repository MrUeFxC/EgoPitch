"""
EgoPitch Core Module - 怒气值引擎
按照 README 公式: Current_Anger = (Trigger_Words × 10) + (Negative_Social_Sentiment × 5)
"""

import logging
from typing import Optional
from openai import OpenAI

logger = logging.getLogger("EgoPitch.AngerEngine")


class AngerEngine:
    """怒气值计算引擎"""

    # 按README公式，基础权重
    TRIGGER_BASE_WEIGHT = 10
    SENTIMENT_WEIGHT = 5

    def __init__(self, client: OpenAI, model: str = "qwen-plus"):
        self.client = client
        self.model = model

    def analyze_question_intensity(self, message: str) -> int:
        """AI分析问题的犀利程度 (0-20分)"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=50,
                messages=[
                    {
                        "role": "system",
                        "content": """你是一个问题分析器。分析主持人问题对球星的攻击性/犀利程度。
返回一个0-20的整数分数：
- 0-5: 友好/普通问题（问候、一般性话题）
- 6-10: 带有轻微质疑或暗示性问题
- 11-15: 直接质疑能力、地位，或有比较性内容
- 16-20: 极具攻击性、直接侮辱、触碰核心痛点

只返回分数数字，不要其他内容。"""
                    },
                    {"role": "user", "content": f"分析这个问题对球星的犀利程度：{message}"}
                ],
            )
            score = int(response.choices[0].message.content.strip())
            return max(0, min(20, score))
        except Exception as e:
            logger.warning(f"AI分析失败: {e}")
            return 0

    def calculate_anger(
        self,
        trigger_score: int,
        message: str,
        social_sentiment: int = 0,
        use_ai_analysis: bool = True
    ) -> int:
        """
        计算怒气增加值

        README公式: Current_Anger = (Trigger_Words × 10) + (Negative_Social_Sentiment × 5)

        这里 trigger_score 已经包含了触发词的分数权重
        """
        # 触发词贡献 (已在StarLoader中按权重计算)
        trigger_contribution = trigger_score

        # AI分析贡献 (叠加)
        ai_score = 0
        if use_ai_analysis:
            ai_score = self.analyze_question_intensity(message)
            logger.debug(f"AI犀利度分析: +{ai_score}")

        # 社交舆论贡献
        sentiment_contribution = social_sentiment * self.SENTIMENT_WEIGHT

        # 问题长度加成
        length_bonus = 0
        if len(message) > 50:
            length_bonus = 3
            logger.debug(f"长问题加成: +{length_bonus}")

        total = trigger_contribution + ai_score + sentiment_contribution + length_bonus

        logger.info(
            f"怒气计算: 触发词({trigger_contribution}) + "
            f"AI分析({ai_score}) + 舆论({sentiment_contribution}) + "
            f"长度({length_bonus}) = {total}"
        )

        return total

    def get_layer_from_anger(self, anger: int) -> int:
        """根据怒气值判断人格层级"""
        if anger >= 80:
            return 3  # 核爆模式
        elif anger >= 40:
            return 2  # 深层自我
        return 1  # 公共人格

    def get_layer_name(self, layer: int) -> str:
        """获取层级名称"""
        names = {
            1: "公共人格",
            2: "深层自我",
            3: "核爆模式"
        }
        return names.get(layer, "未知")