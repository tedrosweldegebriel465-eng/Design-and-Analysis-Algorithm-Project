"""
Database package for the Ethiopian GPS Navigation System.

Exposes SQLAlchemy Base, models, and session helpers.
"""

from src.db.session import Base, get_session  # noqa: F401
from src.db import models  # noqa: F401  (ensure models are imported for metadata)

