from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()

#Create the SQLAlchemy engine.
#The engine manages connections between RepoPulse and PostgreSQL.

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

# SessionLocal is a factory used to create database sessions.
# Each session is used for database reads/write during application work.

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)