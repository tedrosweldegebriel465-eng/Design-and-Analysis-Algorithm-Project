"""
SQLAlchemy ORM models for cities and roads.

These mirror the core domain objects in ``src.graph.city`` and
``src.graph.road`` so the application can persist and load the road network
from a relational database.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey,
    DateTime,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from src.db.session import Base


class CityDB(Base):
    """Database model for cities."""

    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    region = Column(String(255), nullable=True, index=True)
    latitude = Column(Float, nullable=False, default=0.0)
    longitude = Column(Float, nullable=False, default=0.0)
    population = Column(Integer, nullable=True)
    elevation = Column(Float, nullable=True)
    is_capital = Column(Boolean, nullable=False, default=False)
    timezone = Column(String(64), nullable=False, default="EAT")

    # Relationships
    roads_from = relationship("RoadDB", back_populates="city1", foreign_keys="RoadDB.city1_id")
    roads_to = relationship("RoadDB", back_populates="city2", foreign_keys="RoadDB.city2_id")


class RoadDB(Base):
    """Database model for roads connecting cities."""

    __tablename__ = "roads"

    id = Column(Integer, primary_key=True, index=True)
    city1_id = Column(Integer, ForeignKey("cities.id"), nullable=False, index=True)
    city2_id = Column(Integer, ForeignKey("cities.id"), nullable=False, index=True)
    distance = Column(Float, nullable=False)
    road_type = Column(String(32), nullable=False, default="regional")
    condition = Column(String(32), nullable=False, default="good")
    speed_limit = Column(Integer, nullable=False, default=80)
    lanes = Column(Integer, nullable=False, default=2)
    toll = Column(Boolean, nullable=False, default=False)
    name = Column(String(255), nullable=True)
    terrain_factor = Column(Float, nullable=False, default=1.0)
    seasonal = Column(Boolean, nullable=False, default=False)

    city1 = relationship("CityDB", foreign_keys=[city1_id], back_populates="roads_from")
    city2 = relationship("CityDB", foreign_keys=[city2_id], back_populates="roads_to")


class UserDB(Base):
    """Application user who can save favorite routes."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    routes = relationship("SavedRouteDB", back_populates="user", cascade="all, delete-orphan")


class SavedRouteDB(Base):
    """A saved route (favorite) for a given user."""

    __tablename__ = "saved_routes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    source_city = Column(String(255), nullable=False)
    dest_city = Column(String(255), nullable=False)
    mode = Column(String(32), nullable=False, default="shortest")
    options_json = Column(Text, nullable=True)  # JSON string of options (conditions, regions, etc.)
    distance_km = Column(Float, nullable=True)
    travel_time_hours = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("UserDB", back_populates="routes")

