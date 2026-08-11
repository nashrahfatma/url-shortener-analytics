"""
main.py
-------
Entry point of the application. Defines all API routes:

  POST /api/shorten          -> create a new short URL
  GET  /{short_code}         -> redirect to the original URL (and log a click)
  GET  /api/analytics/{code} -> JSON analytics for one short URL
  GET  /                     -> HTML dashboard (list all URLs + click counts)

Run locally with:
    uvicorn app.main:app --reload

Then open http://127.0.0.1:8000  for the dashboard
and  http://127.0.0.1:8000/docs  for the auto-generated Swagger API docs.
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app import models, schemas, crud
from app.database import engine, get_db

# Creates the SQLite tables on startup if they don't already exist.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener with Analytics",
    description="A simple URL shortener that tracks click analytics per link.",
    version="1.0.0",
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/api/shorten", response_model=schemas.URLResponse, tags=["URLs"])
def shorten_url(request: schemas.URLCreateRequest, http_request: Request, db: Session = Depends(get_db)):
    """
    Creates a shortened version of the given URL.
    """
    db_url = crud.create_short_url(db, str(request.original_url))

    base_url = str(http_request.base_url).rstrip("/")
    return schemas.URLResponse(
        short_code=db_url.short_code,
        original_url=db_url.original_url,
        short_url=f"{base_url}/{db_url.short_code}",
        created_at=db_url.created_at,
    )


@app.get("/api/analytics/{short_code}", response_model=schemas.AnalyticsResponse, tags=["Analytics"])
def get_analytics(short_code: str, db: Session = Depends(get_db)):
    """
    Returns click analytics (total clicks + full click history)
    for a given short code.
    """
    db_url = crud.get_url_by_code(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return schemas.AnalyticsResponse(
        short_code=db_url.short_code,
        original_url=db_url.original_url,
        created_at=db_url.created_at,
        total_clicks=crud.get_click_count(db, db_url.id),
        clicks=db_url.clicks,
    )


@app.get("/{short_code}", tags=["Redirect"])
def redirect_to_original(short_code: str, request: Request, db: Session = Depends(get_db)):
    """
    The core redirect feature: visiting /abc123 sends the user to the
    original long URL, and logs a click event before redirecting.
    """
    db_url = crud.get_url_by_code(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    user_agent = request.headers.get("user-agent")
    crud.record_click(db, db_url, user_agent)

    return RedirectResponse(url=db_url.original_url)


@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
def dashboard(request: Request, db: Session = Depends(get_db)):
    """
    Simple server-rendered dashboard listing every shortened URL
    with its click count, newest first.
    """
    urls = crud.get_all_urls(db)
    base_url = str(request.base_url).rstrip("/")

    url_data = [
        {
            "short_code": u.short_code,
            "original_url": u.original_url,
            "short_url": f"{base_url}/{u.short_code}",
            "click_count": crud.get_click_count(db, u.id),
            "created_at": u.created_at.strftime("%d %b %Y, %I:%M %p"),
        }
        for u in urls
    ]

    return templates.TemplateResponse(
        "index.html", {"request": request, "urls": url_data}
    )
