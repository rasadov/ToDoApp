from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.config import Settings

engine = create_async_engine(
    Settings.DATABASE_URL,
    echo=Settings.DEBUG,
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
Base = declarative_base()


async def get_session() -> AsyncSession:
    """Get session for database"""
    async with SessionLocal() as session:
        yield session
        await session.commit()
