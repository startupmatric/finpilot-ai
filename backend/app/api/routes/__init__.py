from .upload import router as upload_router
from .transactions import router as transactions_router
from .analytics import router as analytics_router
from .chat import router as chat_router
from .auth import router as auth_router

__all__ = [
    'upload_router',
    'transactions_router',
    'analytics_router',
    'chat_router',
    'auth_router'
]