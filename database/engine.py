from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from .base import Base

DATABASE_URL = "sqlite+aiosqlite:///./crm.db"


engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    async with async_session() as session:
        yield session
