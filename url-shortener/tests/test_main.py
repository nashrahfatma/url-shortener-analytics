"""
test_main.py
------------
Basic tests using pytest + FastAPI's TestClient.
Run with:  pytest

Having tests is a strong interview talking point for freshers -
very few fresher projects include them, so it's an easy way to
stand out and show you understand code quality, not just features.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.utils import generate_short_code

# Use a separate in-memory SQLite database for tests, so tests never
# touch your real shortener.db file.
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Swap out the real database with the test database for every request."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Creates fresh tables before each test, drops them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_generate_short_code_length():
    """utils.py: generated code should always be 6 characters by default."""
    code = generate_short_code()
    assert len(code) == 6


def test_generate_short_code_is_random():
    """Two generated codes should (almost always) be different."""
    codes = {generate_short_code() for _ in range(50)}
    assert len(codes) > 1


def test_shorten_url_success():
    """POST /api/shorten should return a short_code and short_url."""
    response = client.post("/api/shorten", json={"original_url": "https://www.example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "short_code" in data
    assert data["original_url"] == "https://www.example.com/"
    assert data["short_url"].endswith(data["short_code"])


def test_shorten_url_invalid_url():
    """POST /api/shorten with an invalid URL should fail validation (422)."""
    response = client.post("/api/shorten", json={"original_url": "not-a-valid-url"})
    assert response.status_code == 422


def test_redirect_to_original_url():
    """Visiting /{short_code} should redirect (307) to the original URL."""
    create_response = client.post("/api/shorten", json={"original_url": "https://www.example.com"})
    short_code = create_response.json()["short_code"]

    redirect_response = client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_response.status_code in (302, 307)
    assert redirect_response.headers["location"] == "https://www.example.com/"


def test_redirect_unknown_code_returns_404():
    response = client.get("/doesnotexist", follow_redirects=False)
    assert response.status_code == 404


def test_analytics_tracks_clicks():
    """Analytics should reflect the number of times a short URL was visited."""
    create_response = client.post("/api/shorten", json={"original_url": "https://www.example.com"})
    short_code = create_response.json()["short_code"]

    # Visit the short link 3 times
    for _ in range(3):
        client.get(f"/{short_code}", follow_redirects=False)

    analytics_response = client.get(f"/api/analytics/{short_code}")
    assert analytics_response.status_code == 200
    data = analytics_response.json()
    assert data["total_clicks"] == 3
    assert len(data["clicks"]) == 3


def test_analytics_unknown_code_returns_404():
    response = client.get("/api/analytics/doesnotexist")
    assert response.status_code == 404


def test_dashboard_loads():
    """The homepage dashboard should render successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert "URL Shortener" in response.text
