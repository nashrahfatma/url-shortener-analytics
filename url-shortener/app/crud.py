"""
crud.py
-------
CRUD = Create, Read, Update, Delete.
This file contains all the functions that actually talk to the
database. Keeping them separate from the route handlers (main.py)
follows the "separation of concerns" principle - routes handle
HTTP stuff, crud.py handles data stuff. This also makes these
functions independently testable without spinning up the API.
"""

from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models
from app.utils import generate_short_code


def create_short_url(db: Session, original_url: str) -> models.URL:
    """
    Creates a new short URL record.
    Retries with a new random code in the rare event of a collision
    (two random codes matching) - the unique constraint on short_code
    in models.py is what makes this safe to detect.
    """
    while True:
        code = generate_short_code()
        existing = db.query(models.URL).filter(
            models.URL.short_code == code
        ).first()
        if not existing:
            break  # found a code that isn't already used

    db_url = models.URL(short_code=code, original_url=original_url)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


def get_url_by_code(db: Session, short_code: str) -> Optional[models.URL]:
    """Fetch a single URL record by its short code."""
    return db.query(models.URL).filter(
        models.URL.short_code == short_code
    ).first()


def record_click(db: Session, url: models.URL, user_agent: Optional[str]) -> None:
    """
    Logs a click event for a given URL.
    Storing one row per click (rather than just incrementing a counter)
    is what allows the analytics dashboard to show trends over time,
    not just a raw total.
    """
    click = models.ClickEvent(url_id=url.id, user_agent=user_agent)
    db.add(click)
    db.commit()


def get_all_urls(db: Session):
    """Fetch all shortened URLs, most recently created first."""
    return db.query(models.URL).order_by(models.URL.created_at.desc()).all()


def get_click_count(db: Session, url_id: int) -> int:
    """Efficient SQL COUNT instead of loading every row into Python."""
    return db.query(func.count(models.ClickEvent.id)).filter(
        models.ClickEvent.url_id == url_id
    ).scalar()
