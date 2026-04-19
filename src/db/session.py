"""
Database session management for the Ethiopian GPS Navigation System.

Uses SQLAlchemy with a SQLite database by default. The database URL is read
from the central application configuration.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from src.config import get_config

Base = declarative_base()


def _create_engine():
    """Create a SQLAlchemy engine based on application configuration."""
    config = get_config()
    # `echo=False` to avoid noisy SQL logs; can be toggled on for debugging.
    return create_engine(config.database_url, echo=False, future=True)


_engine = _create_engine()
SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)


def get_session() -> Session:
    """
    Return a new SQLAlchemy Session.

    Usage:
        with get_session() as session:
            ...
    """
    return SessionLocal()

