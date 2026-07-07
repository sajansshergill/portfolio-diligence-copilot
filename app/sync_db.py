from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings


def _to_sync_url(url: str) -> str:
    return url.replace("+asyncpg", "").replace("+psycopg", "")


sync_engine = create_engine(_to_sync_url(settings.database_url), pool_pre_ping=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)
