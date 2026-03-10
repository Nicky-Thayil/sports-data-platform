from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from shared.config import get_settings
from sqlalchemy.pool import NullPool

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    poolclass=NullPool,     # Disable SQLAlchemy pooling — PgBouncer handles it
    connect_args={"statement_cache_size": 0},  # Disable statement caching
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session