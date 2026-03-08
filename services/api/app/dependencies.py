"""
Dependencies for the API service.
"""

from shared.db.session import get_db
from shared.redis import get_redis_client

__all__ = ["get_db", "get_redis_client"]