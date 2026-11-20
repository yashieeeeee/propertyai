# PropertyAI — DarGlobal + Wasalt RAG chatbot

React + TypeScript + Vite + Tailwind frontend, FastAPI backend, SQLite storage, local BM25 retrieval (RAG) and a **free** OpenRouter model (`google/gemma-4-26b-a4b-it:free`). One Docker container serves both API and UI.

## Quick start (Docker)
```bash
cp .env.example .env        # put your OPENROUTER_API_KEY in .env
docker compose up --build   # open http://localhost:3000
python scripts/test_questions.py http://localhost:3000   # runs the 8 assignment questions -> test_results.md
```
Without Docker: `cd frontend && npm ci && npm run build && cd .. && pip install -r backend/requirements.txt && uvicorn backend.app:app --port 3000`

## Deploy (Render, free, ~5 min)
1. Push this folder to a GitHub repo (`.env` is git-ignored).
2. Render → New → Blueprint (uses `render.yaml`) or New Web Service → Docker.
3. Set env var `OPENROUTER_API_KEY`. Health check path: `/health`.
4. Open the Render URL, then run `python scripts/test_questions.py <url>`.
Free Render has no persistent disk; the bundled seed + background re-scrape rebuild the dataset on every start, so nothing is lost.

## How the data works
- `backend/seed_data.json`: 21 documents of real public content (15 DarGlobal incl. full pages for Trump International Hotel & Tower Dubai, The Astera, Trump Tower Jeddah, the 38-project directory, press, business lines; 6 Wasalt) captured on 20 Nov 2026 with original URLs. Always loaded, so the bot works even if scraping is blocked.
- `backend/scraper.py` (Requests + BeautifulSoup, optional Playwright via `USE_PLAYWRIGHT=1`): runs in the background at startup (and every 24h), checks robots.txt, rate-limits itself, **never bypasses bot challenges** (skips and logs). Scraped pages replace seed rows with the same URL.
  Run manually (needs `pip install -r backend/requirements.txt` first) and refresh the seed: `python -m backend.scraper --export`. DarGlobal's bot protection (Incapsula) blocks some pages even from normal IPs; those are skipped, never bypassed, and covered by the seed.
- Wasalt's site blocks automated fetching in some environments; if the live scrape is blocked, the seed (taken from Wasalt's public pages and clearly-labelled third-party descriptions) is used. See Limitations.

## RAG pipeline
Pages are cleaned and split into ~900-char chunks (titles weighted) → BM25 ranking → source-aware routing (naming one company boosts it; "compare"/both guarantees chunks from both) → follow-up questions borrow the previous question → top chunks are grouped into numbered passages → grounded system prompt (answer only from context, cite `[n]`, separate DarGlobal vs Wasalt, never invent prices) → OpenRouter. Citations returned to the UI are the passages the model actually cited.

## API
`GET /health` · `GET /api/sources` · `POST /api/chat {message, history[{role: user|assistant, content}]}`. Validation (system role rejected), per-IP rate limit, CORS, retries + fallback model on 429/5xx, logging.

## Tests
`pip install pytest httpx && pytest tests` (retrieval + API with mocked OpenRouter).

## Limitations
- Prices/payment plans are mostly not published by either site; the bot says so.
- Free OpenRouter models are rate-limited; the UI shows a clear message and the backend retries/falls back.
- Retrieval is lexical (BM25), not embedding-based — chosen for zero cost and fast deploys.
- `openrouter/free` as fallback is an OpenRouter router id; change `OPENROUTER_FALLBACK_MODELS` if it is unavailable.
