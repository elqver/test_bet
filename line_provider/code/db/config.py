from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
import os

dbname = os.getenv("POSTGRES_DB")
username = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")

DB_URL = (
    f"postgresql+asyncpg://{username}:{password}@line-provider-db:5432/{dbname}")

engine = create_async_engine(DB_URL, future=True, echo=False)
async_session = sessionmaker(engine,
                             expire_on_commit=False,
                             class_=AsyncSession)
Base = declarative_base()


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
