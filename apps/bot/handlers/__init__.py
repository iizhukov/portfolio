from .common import router as common_router
from .commands import router as commands_router
from .status import router as status_router
from .history import router as history_router

__all__ = ["common_router", "commands_router", "status_router", "history_router"]

