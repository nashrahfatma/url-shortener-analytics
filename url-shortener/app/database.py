"""
database.py
------------
Sets up the SQLAlchemy database engine and session.
Uses SQLite so the project runs with zero external setup
(no need to install Postgres/MySQL locally).

In an interview you can say: "I used SQLAlchemy as the ORM
layer so the app isn't tightly coupled to SQLite - swapping
to PostgreSQL for production only requires changing the
DATABASE_URL, no code changes."
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database file will be created in the project root as "shortener.db"
DATABASE_URL = "sqlite:///./shortener.db"

# connect_args is only needed for SQLite (allows use across threads,
# which FastAPI's async request handling requires)
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Each request gets its own database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that our ORM models (in models.py) will inherit from
Base = declarative_base()


def get_db():
    """
    Dependency function used by FastAPI routes to get a DB session.
    Ensures the session is always closed after the request finishes,
    even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
