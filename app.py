"""
EgoPitch Backend - AI-powered Star Interview Simulator
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI

load_dotenv()

# ============ 日志配置 ============
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 创建日志格式
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 配置根日志
logging.basicConfig(
    level=logging.DEBUG,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        # 终端输出（INFO及以上）
        logging.StreamHandler(),
        # 文件输出（所有级别）
        logging.FileHandler(
            f"{LOG_DIR}/egopitch_{datetime.now().strftime('%Y%m%d')}.log",
            encoding="utf-8"
        ),
    ]
)

# 获取logger
logger = logging.getLogger("EgoPitch")
logger.info("=" * 50)
logger.info("EgoPitch 服务启动")
logger.info("=" * 50)

# ============ FastAPI 应用 ============
app = FastAPI(title="EgoPitch - Star Interview Simulator")

# Initialize OpenAI client with DashScope config
logger.debug(f"DASHSCOPE_BASE_URL: {os.getenv('DASHSCOPE_BASE_URL')}")
logger.debug(f"API Key 已配置: {bool(os.getenv('DASHSCOPE_API_KEY'))}")

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
)
logger.info("OpenAI 客户端初始化完成")

# ============ 游戏状态 ============
class GameState:
    anger: int = 0
    layer: int = 1
    history: list = []

state = GameState()
logger.debug("游戏状态初始化: anger=0, layer=1")

# ============ 触发词配置（按犀利程度分级） ============
# 重度触发词：直接攻击核心自尊
HEAVY_TRIGGERS = ["替补", "替补席", "坐板凳", "废物", "垃圾", "没用", "踢出去"]

# 中度触发词：质疑能力和地位
MEDIUM_TRIGGERS = ["梅西", "下滑", "老了", "过气", "不如", "比不过", "输给", "被淘汰"]

# 轻度触发词：暗示性批评
LIGHT_TRIGGERS = ["质疑", "批评", "争议", "问题", "为什么", "怎么", "难道", "是不是", "有没有"]

logger.debug(f"触发词配置: 重度={HEAVY_TRIGGERS}, 中度={MEDIUM_TRIGGERS}, 轻度={LIGHT_TRIGGERS}")

LAYER_NAMES = {1: "公共人格", 2: "深层自我", 3: "核爆模式"}

# ============ 核心函数 ============
def get_system_prompt(layer: int, anger: int) -> str:
    """Generate system prompt based on current personality layer."""
    logger.debug(f"生成系统提示: layer={layer}, anger={anger}")

    base_prompt = """你是C罗(Cristiano Ronaldo)，世界著名足球运动员。你现在正在接受一位访谈主持人的采访。

重要规则：
1. 用中文回复，语气要符合当前情绪状态
2. 保持C罗的性格特点：极度自信、重视成就、对质疑敏感
3. 回复要简短有力（1-3句话），不要长篇大论
4. 当被触发时，情绪会升级"""

    layer_instructions = {
        1: """
当前状态：【公共人格】
- 语气：职业化、官方、礼貌
- 表现：回避争议话题，强调团队精神
- 不会直接攻击任何人
- 典型回复风格："感谢提问，我一直在为球队付出..."
""",
        2: """
当前状态：【深层自我】
- 语气：变得强硬、开始引用个人荣誉
- 表现：提到自己的成就（5个金球奖、欧洲杯冠军等）
- 对质疑开始表现出不满
- 典型回复风格："我踢了20年顶级足球，那些质疑我的人请看看我的数据..."
""",
        3: """
当前状态：【核爆模式】⚠️
- 语气：愤怒、爆发、不再掩饰
- 表现：直接批评教练/队友/媒体，爆料更衣室内幕
- 可能说出爆炸性言论
- 不再维护形象，只想发泄
- 典型回复风格："够了！我不想再听这些废话！他们背叛了我！"
"""
    }

    return base_prompt + layer_instructions[layer] + f"\n当前怒气值：{anger}%"


def analyze_question_intensity(message: str) -> int:
    """Use AI to analyze the intensity/s aggressiveness of the question."""
    try:
        response = client.chat.completions.create(
            model="qwen-plus",
            max_tokens=50,
            messages=[
                {
                    "role": "system",
                    "content": """你是一个问题分析器。分析主持人问题对C罗的攻击性/犀利程度。
返回一个0-20的整数分数：
- 0-5: 友好/普通问题（如问候、一般性话题）
- 6-10: 带有轻微质疑或暗示性问题
- 11-15: 直接质疑能力、地位，或有比较性内容
- 16-20: 极具攻击性、直接侮辱、触碰核心痛点

只返回分数数字，不要其他内容。"""
                },
                {"role": "user", "content": f"分析这个问题对C罗的犀利程度：{message}"}
            ],
        )
        score = int(response.choices[0].message.content.strip())
        logger.debug(f"AI 分析犀利程度: {message[:30]}... -> 分数 {score}")
        return max(0, min(20, score))  # 确保在 0-20 范围内
    except Exception as e:
        logger.warning(f"AI 分析失败，使用关键词计算: {e}")
        return None


def calculate_anger(message: str) -> int:
    """Calculate anger increase based on trigger words and question intensity."""
    anger_increase = 0
    triggered_details = []

    # 重度触发词：每个 +15
    for word in HEAVY_TRIGGERS:
        if word in message:
            anger_increase += 15
            triggered_details.append(f"重度:{word}(+15)")

    # 中度触发词：每个 +10
    for word in MEDIUM_TRIGGERS:
        if word in message:
            anger_increase += 10
            triggered_details.append(f"中度:{word}(+10)")

    # 轻度触发词：每个 +5
    for word in LIGHT_TRIGGERS:
        if word in message:
            anger_increase += 5
            triggered_details.append(f"轻度:{word}(+5)")

    # AI 分析犀利程度（叠加）
    ai_score = analyze_question_intensity(message)
    if ai_score is not None:
        anger_increase += ai_score
        triggered_details.append(f"AI分析(+{ai_score})")

    # 问题长度加成：长问题可能包含更多攻击内容
    if len(message) > 50:
        anger_increase += 3
        triggered_details.append("长问题(+3)")

    if triggered_details:
        logger.info(f"怒气增加明细: {triggered_details} -> 总计 +{anger_increase}")
    else:
        logger.debug(f"未检测到触发内容，怒气增加 0")

    return anger_increase


def get_current_layer() -> int:
    """Determine personality layer based on anger level."""
    if state.anger >= 80:
        return 3
    elif state.anger >= 40:
        return 2
    return 1


# ============ API 数据模型 ============
class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    anger: int
    layer: int
    layer_name: str
    anger_increase: int  # 本次怒气增加值


# ============ API 路由 ============
@app.post("/api/chat", response_model=ChatResponse)
async def chat(msg: ChatMessage):
    """Process message with AI and return response."""
    logger.info(f"收到用户消息: {msg.message[:50]}...")

    # Update anger
    anger_increase = calculate_anger(msg.message)
    old_anger = state.anger
    state.anger = min(100, state.anger + anger_increase)
    old_layer = state.layer
    state.layer = get_current_layer()

    if state.layer != old_layer:
        logger.warning(f"人格层级变化: {LAYER_NAMES[old_layer]} -> {LAYER_NAMES[state.layer]}")
    logger.debug(f"怒气值变化: {old_anger} -> {state.anger}")

    # Add user message to history
    state.history.append({"role": "user", "content": f"主持人：{msg.message}"})
    logger.debug(f"对话历史长度: {len(state.history)}")

    # Call AI
    try:
        logger.debug("调用 AI API...")
        system_prompt = get_system_prompt(state.layer, state.anger)

        response = client.chat.completions.create(
            model="qwen-plus",
            max_tokens=150,
            messages=[
                {"role": "system", "content": system_prompt},
                *state.history
            ],
        )
        ai_response = response.choices[0].message.content
        logger.info(f"AI 响应成功: {ai_response[:80]}...")
        logger.debug(f"API 响应详情: model={response.model}, tokens={response.usage}")

    except Exception as e:
        logger.error(f"AI API 调用失败: {type(e).__name__}: {e}")
        ai_response = f"[AI暂时无法响应] 错误: {str(e)[:100]}"

    # Add AI response to history
    state.history.append({"role": "assistant", "content": ai_response})

    # Gradual anger decay
    state.anger = max(0, state.anger - 3)
    logger.debug(f"怒气衰减后: {state.anger}")

    result = ChatResponse(
        response=ai_response,
        anger=state.anger,
        layer=state.layer,
        layer_name=LAYER_NAMES[state.layer],
        anger_increase=anger_increase,
    )
    logger.debug(f"返回结果: anger={result.anger}, anger_increase={result.anger_increase}, layer={result.layer_name}")

    return result


@app.post("/api/reset")
async def reset():
    """Reset game state."""
    logger.info("游戏状态重置")
    state.anger = 0
    state.layer = 1
    state.history = []
    return {"status": "ok", "message": "状态已重置"}


@app.get("/api/state")
async def get_state():
    """Get current game state."""
    return {
        "anger": state.anger,
        "layer": state.layer,
        "layer_name": LAYER_NAMES[state.layer],
    }


@app.get("/", response_class=HTMLResponse)
async def root():
    logger.debug("访问首页")
    return open("static/index.html", encoding="utf-8").read()


# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")