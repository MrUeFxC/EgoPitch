"""
EgoPitch Backend - AI-powered Star Interview Simulator
按照 README.md 架构设计重构
"""

import os
import logging
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI

# 导入核心模块
from core.star_loader import StarLoader
from core.anger_engine import AngerEngine
from core.social_pulse import SocialPulse, Comment

load_dotenv()

# ============ 日志配置 ============
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.DEBUG,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            f"{LOG_DIR}/egopitch_{datetime.now().strftime('%Y%m%d')}.log",
            encoding="utf-8"
        ),
    ]
)

logger = logging.getLogger("EgoPitch")
logger.info("=" * 50)
logger.info("EgoPitch 服务启动 - README架构设计")
logger.info("=" * 50)

# ============ FastAPI 应用 ============
app = FastAPI(title="EgoPitch - Star Interview Simulator")

# 初始化客户端
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
)
logger.info("OpenAI 客户端初始化完成")

# 加载球星配置
StarLoader.load_all()
stars = StarLoader.get_all_stars()
if not stars:
    logger.error("未加载任何球星配置！请检查 configs/stars/ 目录")

# 初始化核心引擎
anger_engine = AngerEngine(client)
social_pulse = SocialPulse(client)


# ============ 游戏状态管理 ============
class InterviewSession:
    """访谈会话状态"""

    def __init__(self, star_id: str = "cr7"):
        self.star = StarLoader.get_star(star_id)
        if not self.star:
            raise ValueError(f"球星配置不存在: {star_id}")

        self.anger = 0
        self.layer = 1
        self.history: List[dict] = []
        self.pulse_comments: List[Comment] = []
        self.phase = 1  # 访谈阶段

        logger.info(f"创建访谈会话: {self.star.name}")

    def update_anger(self, message: str) -> int:
        """更新怒气值"""
        # 触发词贡献
        trigger_score = self.star.calculate_trigger_anger(message)

        # 社交舆论贡献
        sentiment = social_pulse.get_sentiment_value()

        # 综合计算
        anger_increase = anger_engine.calculate_anger(
            trigger_score=trigger_score,
            message=message,
            social_sentiment=sentiment
        )

        old_anger = self.anger
        self.anger = min(100, self.anger + anger_increase)

        # 更新层级
        old_layer = self.layer
        self.layer = anger_engine.get_layer_from_anger(self.anger)

        if self.layer != old_layer:
            logger.warning(
                f"人格层级变化: {anger_engine.get_layer_name(old_layer)} -> "
                f"{anger_engine.get_layer_name(self.layer)}"
            )

        logger.info(f"怒气值: {old_anger} -> {self.anger} (+{anger_increase})")
        return anger_increase

    def decay_anger(self):
        """怒气自然衰减"""
        self.anger = max(0, self.anger - 3)
        self.layer = anger_engine.get_layer_from_anger(self.anger)

    def get_system_prompt(self) -> str:
        """获取当前人格的系统提示"""
        return self.star.get_layer_prompt(self.layer, self.anger)

    def reset(self):
        """重置会话"""
        self.anger = 0
        self.layer = 1
        self.history = []
        self.pulse_comments = []
        self.phase = 1
        social_pulse.reset_sentiment()
        logger.info("会话已重置")


# 全局会话（单球星模式）
session: Optional[InterviewSession] = None


def get_session() -> InterviewSession:
    """获取或创建会话"""
    global session
    if session is None:
        session = InterviewSession("cr7")
    return session


# ============ API 数据模型 ============
class ChatMessage(BaseModel):
    message: str
    star_id: Optional[str] = "cr7"


class ChatResponse(BaseModel):
    response: str
    anger: int
    layer: int
    layer_name: str
    anger_increase: int
    comments: List[dict] = []
    star_name: str


class CommentsResponse(BaseModel):
    comments: List[dict]
    sentiment: int


class StarInfo(BaseModel):
    id: str
    name: str
    description: str


# ============ API 路由 ============
@app.get("/api/stars", response_model=List[StarInfo])
async def list_stars():
    """获取所有球星列表"""
    stars = StarLoader.get_all_stars()
    return [
        StarInfo(id=s.id, name=s.name, description=s.description)
        for s in stars
    ]


@app.post("/api/select_star")
async def select_star(star_id: str):
    """选择球星"""
    global session
    session = InterviewSession(star_id)
    return {"status": "ok", "star": session.star.name}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(msg: ChatMessage):
    """处理聊天消息"""
    sess = get_session()
    logger.info(f"[{sess.star.name}] 收到消息: {msg.message[:50]}...")

    # 更新怒气值
    anger_increase = sess.update_anger(msg.message)

    # 添加用户消息到历史
    sess.history.append({"role": "user", "content": f"主持人：{msg.message}"})

    # 调用AI生成回复
    try:
        logger.debug("调用 AI API...")
        response = client.chat.completions.create(
            model="qwen-plus",
            max_tokens=150,
            messages=[
                {"role": "system", "content": sess.get_system_prompt()},
                *sess.history
            ],
        )
        ai_response = response.choices[0].message.content
        logger.info(f"AI 响应: {ai_response[:80]}...")

    except Exception as e:
        logger.error(f"AI 调用失败: {e}")
        ai_response = f"[AI响应失败] {str(e)[:100]}"

    # 添加AI回复到历史
    sess.history.append({"role": "assistant", "content": ai_response})

    # 怒气衰减
    sess.decay_anger()

    # 根据阶段生成舆论评论
    comments = []
    if sess.layer >= 2:
        # 深层自我及以上，注入评论刺激
        pulse_comments = social_pulse.generate_comments(
            topic=msg.message,
            count=2,
            star_name=sess.star.name
        )
        comments = [
            {"content": c.content, "likes": c.likes, "type": c.type}
            for c in pulse_comments
        ]
        sess.pulse_comments.extend(pulse_comments)

    # 更新访谈阶段
    if sess.anger > 60 and sess.phase < 3:
        sess.phase = 3
        logger.info(f"进入深挖阶段")
    elif sess.anger > 80 and sess.phase < 4:
        sess.phase = 4
        logger.warning(f"进入引爆阶段！")

    return ChatResponse(
        response=ai_response,
        anger=sess.anger,
        layer=sess.layer,
        layer_name=anger_engine.get_layer_name(sess.layer),
        anger_increase=anger_increase,
        comments=comments,
        star_name=sess.star.name
    )


@app.get("/api/comments", response_model=CommentsResponse)
async def get_comments(topic: Optional[str] = None):
    """获取舆论评论"""
    sess = get_session()
    comments = social_pulse.generate_comments(
        topic=topic,
        count=3,
        star_name=sess.star.name
    )

    return CommentsResponse(
        comments=[
            {"content": c.content, "likes": c.likes, "type": c.type}
            for c in comments
        ],
        sentiment=social_pulse.get_sentiment_value()
    )


@app.post("/api/reset")
async def reset():
    """重置游戏"""
    sess = get_session()
    sess.reset()
    return {"status": "ok", "message": "访谈已重置"}


@app.get("/api/state")
async def get_state():
    """获取当前状态"""
    sess = get_session()
    return {
        "anger": sess.anger,
        "layer": sess.layer,
        "layer_name": anger_engine.get_layer_name(sess.layer),
        "phase": sess.phase,
        "star": sess.star.name,
        "sentiment": social_pulse.get_sentiment_value()
    }


@app.get("/", response_class=HTMLResponse)
async def root():
    """首页"""
    return open("static/index.html", encoding="utf-8").read()


# 挂载静态文件
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")