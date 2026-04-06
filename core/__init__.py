"""
EgoPitch Core Module
核心功能模块包
"""

from .star_loader import StarLoader, StarConfig
from .anger_engine import AngerEngine
from .social_pulse import SocialPulse, Comment

__all__ = [
    "StarLoader",
    "StarConfig",
    "AngerEngine",
    "SocialPulse",
    "Comment"
]