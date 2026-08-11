RL Shortener with Analytics Dashboard
A backend service that shortens long URLs and tracks click analytics for each link — built with FastAPI, SQLAlchemy, and SQLite.

Live demo of what it does:

Paste a long URL into the dashboard → get back a short link.
Every time someone visits the short link, they're redirected to the original URL and a click event is logged (timestamp + browser).
View real analytics for any link: total clicks and full click history.
