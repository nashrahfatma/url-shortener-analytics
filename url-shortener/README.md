# URL Shortener with Analytics Dashboard

A backend service that shortens long URLs and tracks click analytics
for each link — built with **FastAPI**, **SQLAlchemy**, and **SQLite**.

Live demo of what it does:
1. Paste a long URL into the dashboard → get back a short link.
2. Every time someone visits the short link, they're redirected to the
   original URL **and** a click event is logged (timestamp + browser).
3. View real analytics for any link: total clicks and full click history.

---

## Why this project (talking points for interviews)

- **REST API design** — clean separation between routes (`main.py`),
  business/data logic (`crud.py`), database models (`models.py`), and
  request/response validation (`schemas.py`). This is the standard
  layered architecture used in real production backends.
- **Relational database design** — a one-to-many relationship between
  `URL` and `ClickEvent` (one URL has many clicks), which is what
  makes real analytics (not just a counter) possible. Good example to
  discuss database normalization.
- **Automated testing** — `tests/test_main.py` covers URL creation,
  redirection, 404 handling, and analytics tracking using `pytest`.
- **Input validation** — Pydantic validates that submitted URLs are
  well-formed before they ever touch the database.
- **Collision handling** — short code generation checks for duplicates
  before saving, so two links can never collide.

---

## Tech Stack

| Layer          | Technology                 |
|----------------|-----------------------------|
| Backend        | Python, FastAPI             |
| Database       | SQLite (via SQLAlchemy ORM) |
| Frontend       | HTML, CSS, vanilla JS       |
| Testing        | Pytest, FastAPI TestClient  |

---

## Project Structure

```
url-shortener/
├── app/
│   ├── __init__.py
│   ├── main.py         # FastAPI routes (API + dashboard)
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── crud.py            # Database read/write operations
│   ├── database.py         # DB engine & session setup
│   └── utils.py              # Short code generator
├── templates/
│   └── index.html               # Dashboard HTML (Jinja2)
├── static/
│   ├── style.css                  # Dashboard styling
│   └── script.js                    # Dashboard JS (calls the API)
├── tests/
│   └── test_main.py                    # Automated tests
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Setup & Run Locally (VS Code)

**1. Open the folder in VS Code**, then open a terminal (`` Ctrl + ` ``).

**2. Create and activate a virtual environment:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Run the server:**
```bash
uvicorn app.main:app --reload
```

**5. Open in your browser:**
- Dashboard: http://127.0.0.1:8000
- Interactive API docs (Swagger UI): http://127.0.0.1:8000/docs

The SQLite database file (`shortener.db`) is created automatically the
first time you run the app — no manual database setup needed.

---

## Running Tests

```bash
pytest -v
```

This runs 8 tests covering short code generation, URL creation,
redirection, 404 handling, and click analytics.

---

## API Endpoints

| Method | Endpoint                     | Description                          |
|--------|-------------------------------|---------------------------------------|
| POST   | `/api/shorten`                | Create a short URL                    |
| GET    | `/{short_code}`               | Redirect to original URL (logs click) |
| GET    | `/api/analytics/{short_code}` | Get click analytics for a URL         |
| GET    | `/`                            | HTML dashboard                        |

Example request (using `curl`):
```bash
curl -X POST http://127.0.0.1:8000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://www.google.com"}'
```

---

## Deploying (free options)

- **Render.com** — connect your GitHub repo, set the start command to
  `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, and it deploys
  automatically on every push.
- **Railway.app** — similar one-click deploy from GitHub.

Once deployed, update the README with your live URL — a working link
on your resume matters more than the GitHub repo alone.

---

## Possible Future Improvements

(Good answers if an interviewer asks "what would you add next?")
- Custom short codes (let users pick their own alias)
- Rate limiting to prevent abuse
- Link expiration dates
- User accounts so people can manage their own links
- Redis caching for high-traffic redirects
