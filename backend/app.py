"""PropertyAI – FastAPI backend: SQLite store + BM25 RAG + OpenRouter (free model)."""
from __future__ import annotations

import json
import logging
import os
import re
import sqlite3
import threading
import time
from collections import defaultdict, deque
from pathlib import Path

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator

from backend.rag import Index

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT.parent / ".env")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("propertyai")

DB_PATH = Path(os.getenv("DB_PATH", str(ROOT.parent / "data" / "propertyai.db")))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
MODEL = os.getenv("OPENROUTER_MODEL", "google/gemma-4-26b-a4b-it:free")
FALLBACKS = [m.strip() for m in os.getenv("OPENROUTER_FALLBACK_MODELS", "google/gemma-4-31b-it:free,nvidia/nemotron-3-ultra-550b-a55b:free,openrouter/free").split(",") if m.strip()]
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
FRONTEND_DIST = Path(os.getenv("FRONTEND_DIST", str(ROOT.parent / "frontend" / "dist")))
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
SCRAPE_ON_START = os.getenv("SCRAPE_ON_START", "true").lower() == "true"
SCRAPE_EVERY_HOURS = float(os.getenv("SCRAPE_EVERY_HOURS", "24"))

index = Index()
_lock = threading.Lock()
state = {"last_scrape": None, "scrape_summary": None, "scraping": False}

# ---------------------------------------------------------------- storage

def db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, timeout=30)
    con.row_factory = sqlite3.Row
    return con


def init_db() -> None:
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY, source TEXT NOT NULL, title TEXT, url TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL, origin TEXT DEFAULT 'seed', retrieved_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        con.execute("CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT)")


def upsert_doc(d: dict) -> None:
    """Scraped content always replaces older content for the same URL."""
    with db() as con:
        con.execute(
            """INSERT INTO documents(source,title,url,content,origin) VALUES(?,?,?,?,?)
               ON CONFLICT(url) DO UPDATE SET title=excluded.title, content=excluded.content,
               origin=excluded.origin, retrieved_at=CURRENT_TIMESTAMP""",
            (d["source"], d["title"], d["url"], d["content"], d.get("origin", "scraped")))


def load_seed() -> int:
    """Insert the bundled snapshot of real public content; never overwrites fresher scraped rows."""
    seed = ROOT / "seed_data.json"
    if not seed.exists():
        return 0
    n = 0
    with db() as con:
        for d in json.loads(seed.read_text()):
            cur = con.execute("INSERT OR IGNORE INTO documents(source,title,url,content,origin) VALUES(?,?,?,?,?)",
                              (d["source"], d["title"], d["url"], d["content"], d.get("origin", "captured")))
            n += cur.rowcount
    return n


def all_docs() -> list[sqlite3.Row]:
    with db() as con:
        return con.execute("SELECT * FROM documents ORDER BY source, title").fetchall()


def rebuild_index() -> None:
    docs = [dict(r) for r in all_docs()]
    with _lock:
        index.build(docs)
    log.info("Index rebuilt: %d documents, %d chunks", len(docs), len(index.chunks))


def scrape_job() -> None:
    if state["scraping"]:
        return
    state["scraping"] = True
    try:
        from backend import scraper
        state["scrape_summary"] = scraper.run(upsert_doc)
        state["last_scrape"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with db() as con:
            con.execute("INSERT OR REPLACE INTO meta VALUES('last_scrape', ?)", (state["last_scrape"],))
        rebuild_index()
    except Exception:
        log.exception("scrape job failed")
    finally:
        state["scraping"] = False


def _scrape_due() -> bool:
    with db() as con:
        r = con.execute("SELECT v FROM meta WHERE k='last_scrape'").fetchone()
    if not r:
        return True
    state["last_scrape"] = r["v"]
    try:
        age = time.time() - time.mktime(time.strptime(r["v"], "%Y-%m-%dT%H:%M:%SZ")) + time.timezone
    except ValueError:
        return True
    return age > SCRAPE_EVERY_HOURS * 3600


# ---------------------------------------------------------------- app

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    log.info("Seeded %d new documents", load_seed())
    rebuild_index()
    if SCRAPE_ON_START and _scrape_due():
        threading.Thread(target=scrape_job, daemon=True).start()
    yield


app = FastAPI(title="PropertyAI API", version="2.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_methods=["GET", "POST", "OPTIONS"],
                   allow_headers=["*"], allow_credentials=False)


_hits: dict[str, deque] = defaultdict(deque)


def rate_limit(request: Request, per_min: int = int(os.getenv("RATE_LIMIT_PER_MIN", "20"))) -> None:
    ip = (request.headers.get("x-forwarded-for") or (request.client.host if request.client else "?")).split(",")[0].strip()
    now, q = time.time(), _hits[ip]
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= per_min:
        raise HTTPException(429, "Too many requests – please wait a moment and try again.")
    q.append(now)


class Turn(BaseModel):
    role: str
    content: str = Field(max_length=4000)

    @field_validator("role")
    @classmethod
    def _role(cls, v: str) -> str:
        if v not in ("user", "assistant"):
            raise ValueError("role must be 'user' or 'assistant'")
        return v


class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=2000)
    history: list[Turn] = Field(default_factory=list, max_length=20)

    @field_validator("message")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("message too short")
        return v


SYSTEM_PROMPT = """You are PropertyAI, a careful real-estate research assistant for two sources: DarGlobal (darglobal.co.uk, an international luxury developer) and Wasalt (wasalt.sa, a Saudi property marketplace).

RULES
1. Answer ONLY from the numbered CONTEXT passages supplied in the user's message. Do not use outside knowledge about these companies or projects.
2. Cite every factual claim with its passage number in square brackets, e.g. [1] or [2][3].
3. Always make clear which company a fact belongs to (write "DarGlobal:" / "Wasalt:" or name the company). Never blend the two.
4. Never invent or estimate prices, availability, payment plans, yields, specifications or dates. If a detail is not in the context, say plainly that it is not available in the collected data and suggest contacting the company or checking the linked page.
5. If the context does not address the question at all, say so briefly instead of guessing.
6. Be concise and well structured: short paragraphs or bullet lists. Use the conversation history only to resolve follow-up references.
7. This is information from public web pages, not financial or legal advice."""


def _clean_key() -> str | None:
    k = (os.getenv("OPENROUTER_API_KEY") or "").strip()
    if k.lower().startswith("bearer "):
        k = k[7:].strip()
    return k or None


def call_openrouter(messages: list[dict], key: str) -> tuple[str, str]:
    """Walk the free-model chain (primary, then fallbacks). A 429/5xx moves straight to the next model;
    after a full pass we wait and try the whole chain once more. Returns (answer, model_used)."""
    chain = [MODEL] + [m for m in FALLBACKS if m != MODEL]
    last_err = "unknown error"
    for round_no in range(2):
        for model in chain:
            try:
                r = requests.post(
                    OPENROUTER_URL,
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                             "HTTP-Referer": os.getenv("APP_URL", "http://localhost:3000"), "X-Title": "PropertyAI"},
                    json={"model": model, "messages": messages, "temperature": 0.1, "max_tokens": 900},
                    timeout=60)
            except requests.RequestException as e:
                last_err = f"{model}: network error {e.__class__.__name__}"
                continue
            if r.status_code == 401:
                raise HTTPException(502, "The AI provider rejected the API key. Check OPENROUTER_API_KEY on the server.")
            if r.status_code != 200:
                last_err = f"{model}: HTTP {r.status_code}"
                log.warning("OpenRouter %s -> %s %s", model, r.status_code, r.text[:160].replace("\n", " "))
                continue
            try:
                content = (r.json()["choices"][0]["message"].get("content") or "").strip()
            except Exception:
                content = ""
            if content:
                return content, model
            last_err = f"{model}: empty response"
            log.warning("OpenRouter %s -> empty content", model)
        if round_no == 0:
            time.sleep(4)
    log.error("All models failed: %s", last_err)
    raise HTTPException(503, "The free AI models are rate-limited right now. Please wait a few seconds and ask again.")


@app.get("/health")
def health() -> dict:
    with db() as con:
        by_source = {r["source"]: r["n"] for r in con.execute("SELECT source, COUNT(*) n FROM documents GROUP BY source")}
        scraped = con.execute("SELECT COUNT(*) FROM documents WHERE origin='scraped'").fetchone()[0]
    return {"status": "ok", "documents": sum(by_source.values()), "documents_by_source": by_source,
            "live_scraped_documents": scraped, "chunks": len(index.chunks), "model": MODEL, "fallback_models": FALLBACKS,
            "openrouter_configured": bool(_clean_key()), "last_scrape": state["last_scrape"],
            "scrape_summary": state["scrape_summary"], "scraping_now": state["scraping"]}


@app.get("/api/sources")
def sources() -> list[dict]:
    return [{"source": r["source"], "title": r["title"], "url": r["url"], "origin": r["origin"],
             "retrieved_at": r["retrieved_at"], "chars": len(r["content"])} for r in all_docs()]


@app.post("/api/chat")
def chat(req: ChatRequest, request: Request) -> dict:
    rate_limit(request)
    key = _clean_key()
    if not key:
        raise HTTPException(503, "The AI service is not configured on this server (missing OPENROUTER_API_KEY).")
    history = [t for t in req.history if t.content.strip()][-6:]
    prev_user = next((t.content for t in reversed(history) if t.role == "user"), None)
    with _lock:
        hits = index.search(req.message, k=8, prev_user=prev_user)

    # number documents (not chunks) so citations map to clickable sources
    doc_order: list[str] = []
    meta: dict[str, dict] = {}
    parts: dict[str, list[str]] = {}
    for _, c in hits:
        if c.url not in meta:
            doc_order.append(c.url)
            meta[c.url] = {"source": c.source, "title": c.title, "url": c.url}
            parts[c.url] = []
        parts[c.url].append(c.text)
    if doc_order:
        context = "\n\n".join(
            f"[{i + 1}] SOURCE: {meta[u]['source']} | {meta[u]['title']} | {u}\n" + "\n".join(parts[u])
            for i, u in enumerate(doc_order))
    else:
        context = "(no relevant passages were found in the collected data)"

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [{"role": t.role, "content": t.content[:1500]} for t in history]
    messages.append({"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION: {req.message}"})

    answer, used = call_openrouter(messages, key)
    answer = answer.replace("【", "[").replace("】", "]")  # some models use full-width brackets
    cited_idx = sorted({int(n) for n in re.findall(r"\[(\d{1,2})\]", answer) if 1 <= int(n) <= len(doc_order)})
    cited = [{**meta[doc_order[i - 1]], "n": i} for i in cited_idx]
    retrieved = [{**meta[u], "n": i + 1} for i, u in enumerate(doc_order)]
    log.info("chat q=%r retrieved=%d cited=%s model=%s", req.message[:80], len(doc_order), cited_idx, used)
    fallback, seen = [], set()
    for r_ in retrieved:  # no explicit citations: show the best doc of each source rather than one company only
        if r_["source"] not in seen:
            fallback.append(r_)
            seen.add(r_["source"])
    fallback = (fallback + [r_ for r_ in retrieved if r_ not in fallback])[:3]
    return {"answer": answer, "sources": cited or fallback, "cited": bool(cited), "retrieved": retrieved,
            "model": used}


# ---------------------------------------------------------------- static frontend (single-container deploy)
if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        if path.startswith(("api/", "health")):
            return JSONResponse({"detail": "Not found"}, status_code=404)
        target = (FRONTEND_DIST / path).resolve()
        if path and target.is_file() and FRONTEND_DIST.resolve() in target.parents:
            return FileResponse(target)
        return FileResponse(FRONTEND_DIST / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "3000")))
