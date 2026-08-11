"""
schemas.py
----------
Pydantic models define the "shape" of data going IN to the API
(requests) and OUT of the API (responses). FastAPI uses these to:
  - validate incoming request bodies automatically
  - auto-generate the interactive API docs (Swagger UI at /docs)
  - serialize database objects into clean JSON responses

Keeping schemas separate from ORM models (models.py) is a deliberate
design choice: it means the API's public contract can evolve
independently of the internal database structure.
"""

from pydantic import BaseModel, HttpUrl, ConfigDict
from datetime import datetime
from typing import List, Optional


class URLCreateRequest(BaseModel):
    """What the client sends when creating a short URL."""
    original_url: HttpUrl  # Pydantic validates this is a real, well-formed URL


class URLResponse(BaseModel):
    """What we send back after creating a short URL."""
    model_config = ConfigDict(from_attributes=True)

    short_code: str
    original_url: str
    short_url: str  # full shareable link, e.g. http://localhost:8000/abc123
    created_at: datetime


class ClickEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    clicked_at: datetime
    user_agent: Optional[str] = None


class AnalyticsResponse(BaseModel):
    """Full analytics for one short URL."""
    model_config = ConfigDict(from_attributes=True)

    short_code: str
    original_url: str
    created_at: datetime
    total_clicks: int
    clicks: List[ClickEventResponse]
