"""PolyMind API Routers Package."""

from .router import router as router_router
from .synthesis import router as synthesis_router
from .debate import router as debate_router
from .hub import router as hub_router
from .vote import router as vote_router

__all__ = [
    "router_router",
    "synthesis_router",
    "debate_router",
    "hub_router",
    "vote_router",
]
