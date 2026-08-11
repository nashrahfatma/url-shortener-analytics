"""
models.py
---------
Defines the database tables using SQLAlchemy's ORM.

Two tables:
  1. URL          - stores the mapping between a short code and the
                     original long URL.
  2. ClickEvent    - stores one row PER CLICK, so we can build real
                     analytics (clicks over time, not just a total count).

This one-to-many relationship (one URL -> many ClickEvents) is a good
talking point in interviews about database design / normalization.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String(10), unique=True, index=True, nullable=False)
    original_url = Column(String(2048), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # One URL can have many click events.
    # cascade="all, delete-orphan" means if a URL is deleted,
    # its click history is deleted too (keeps the DB clean).
    clicks = relationship(
        "ClickEvent", back_populates="url", cascade="all, delete-orphan"
    )

    @property
    def click_count(self) -> int:
        """Convenience property: total number of clicks for this URL."""
        return len(self.clicks)


class ClickEvent(Base):
    __tablename__ = "click_events"

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    clicked_at = Column(DateTime, default=datetime.utcnow)
    user_agent = Column(String(512), nullable=True)

    url = relationship("URL", back_populates="clicks")
