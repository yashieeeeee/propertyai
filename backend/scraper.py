"""Polite scraper for darglobal.co.uk and wasalt.sa (Requests + BeautifulSoup).

- Checks robots.txt before every fetch and identifies itself honestly.
- Never tries to bypass CAPTCHAs, bot challenges (e.g. Incapsula) or logins: a blocked page is skipped and logged.
- Optional Playwright rendering (USE_PLAYWRIGHT=1) for JavaScript-only pages.

CLI:  python -m backend.scraper            # scrape into the SQLite DB
      python -m backend.scraper --export   # also write backend/seed_data.json from the result
"""
from __future__ import annotations

import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from urllib import robotparser
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup

log = logging.getLogger("scraper")
UA = "Mozilla/5.0 (compatible; PropertyAIBot/1.0; research assistant, respects robots.txt)"
DELAY = float(os.getenv("SCRAPE_DELAY", "1.0"))
MAX_DARGLOBAL = int(os.getenv("SCRAPE_MAX_DARGLOBAL", "60"))
MAX_WASALT = int(os.getenv("SCRAPE_MAX_WASALT", "25"))
BLOCK_MARKERS = ("incapsula", "_incapsula_", "captcha", "access denied", "request unsuccessful", "just a moment", "attention required")
CUT_MARKERS = ("Register Your Interest", "FOLLOW US ON", "Discover exclusive luxury real estate and investment opportunities")
NOISE = {"gallery", "view all images", "download brochure", "show more", "english", "العربية", "book unit", "play", "mute"}

_session = requests.Session()
_session.headers.update({"User-Agent": UA, "Accept-Language": "en"})
_robots: dict[str, robotparser.RobotFileParser | None] = {}


class Blocked(Exception):
    pass


def allowed(url: str) -> bool:
    host = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    if host not in _robots:
        rp = robotparser.RobotFileParser()
        try:
            r = _session.get(host + "/robots.txt", timeout=15)
            if r.status_code == 200 and "<html" not in r.text[:200].lower():
                rp.parse(r.text.splitlines())
                _robots[host] = rp
            else:
                _robots[host] = None  # no usable robots.txt -> no explicit restriction
        except requests.RequestException:
            _robots[host] = None
    rp = _robots[host]
    return True if rp is None else rp.can_fetch(UA, url)


def fetch(url: str) -> str:
    if not allowed(url):
        raise Blocked(f"robots.txt disallows {url}")
    if os.getenv("USE_PLAYWRIGHT") == "1":
        html = _fetch_playwright(url)
    else:
        r = _session.get(url, timeout=25)
        if r.status_code in (401, 403, 429, 503):
            raise Blocked(f"HTTP {r.status_code} for {url}")
        r.raise_for_status()
        html = r.text
    head = html[:4000].lower()
    if any(m in head for m in BLOCK_MARKERS) and len(html) < 20000:
        raise Blocked(f"bot challenge detected at {url}")
    return html


def _fetch_playwright(url: str) -> str:  # optional, only if installed
    from playwright.sync_api import sync_playwright  # type: ignore

    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(user_agent=UA)
        page.goto(url, wait_until="networkidle", timeout=45000)
        html = page.content()
        b.close()
    return html


def clean(html: str) -> tuple[str, str, str]:
    """Return (title, meta_description, cleaned_text)."""
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.title.string or "").strip() if soup.title and soup.title.string else ""
    md = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
    desc = (md.get("content") or "").strip() if md else ""
    for t in soup(["script", "style", "noscript", "nav", "header", "footer", "form", "svg", "iframe", "img", "video", "button", "select"]):
        t.decompose()
    root = soup.find("main") or soup.body or soup
    lines, seen = [], set()
    for ln in root.get_text("\n", strip=True).splitlines():
        ln = re.sub(r"\s+", " ", ln).strip()
        if not ln or ln.lower() in NOISE:
            continue
        if any(ln.startswith(m) for m in CUT_MARKERS):
            break
        if len(ln) > 25 and ln in seen:
            continue
        seen.add(ln)
        lines.append(ln)
    return title, desc, "\n".join(lines)


def _links(html: str, base: str, host: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["header", "footer", "nav", "script", "style"]):
        t.decompose()
    out = []
    for a in soup.find_all("a", href=True):
        u = urldefrag(urljoin(base, a["href"]))[0].rstrip("/")
        p = urlparse(u)
        if p.netloc.replace("www.", "") == host and u not in out and not re.search(r"\.(pdf|jpg|png|webp|mp4)$", u, re.I):
            out.append(u)
    return out


def _doc(source: str, url: str, html: str) -> dict | None:
    title, desc, text = clean(html)
    body = (desc + "\n" + text).strip() if desc and desc not in text else text
    if len(body) < 250:
        return None
    return dict(source=source, title=title.split("|")[0].strip() or url, url=url, content=body[:14000], origin="scraped")


def scrape_darglobal() -> list[dict]:
    host, base = "darglobal.co.uk", "https://darglobal.co.uk"
    docs, done = [], set()
    queue: list[str] = []
    try:
        proj_html = fetch(base + "/projects")
        proj_links = [u for u in _links(proj_html, base + "/projects", host)
                      if not re.search(r"/(projects|privacy-policy|press|investor|about|product-category|partners)$", u) and u != base]
        queue += proj_links
        d = _doc("DarGlobal", base + "/projects", proj_html)
        if d:
            d["title"] = "DarGlobal – project directory"
            docs.append(d)
            done.add(base + "/projects")
    except Exception as e:
        log.warning("DarGlobal projects page: %s", e)
    try:
        home = fetch(base + "/")
        d = _doc("DarGlobal", base + "/", home)
        if d:
            docs.append(d)
            done.add(base + "/")
        queue += [u for u in _links(home, base, host) if "/press/" in u][:6]
    except Exception as e:
        log.warning("DarGlobal home: %s", e)
    queue += [f"{base}/{p}" for p in ("about", "why-invest", "investor", "press", "hospitality", "luxury-golf-communities", "commercial", "tokenization", "exclusive-membership")]
    for u in queue:
        if u in done or len(docs) >= MAX_DARGLOBAL:
            continue
        done.add(u)
        time.sleep(DELAY)
        try:
            d = _doc("DarGlobal", u, fetch(u))
            if d:
                docs.append(d)
                log.info("DarGlobal ✓ %s", u)
        except Blocked as e:
            log.warning("DarGlobal blocked: %s", e)
        except Exception as e:
            log.warning("DarGlobal skip %s: %s", u, e)
    return docs


def scrape_wasalt() -> list[dict]:
    base, host = "https://wasalt.sa", "wasalt.sa"
    docs, done = [], set()
    queue = [f"{base}/en", f"{base}/en/corporate", f"{base}/en/properties-for-rent-in-saudi-arabia",
             f"{base}/en/properties-for-rent-in-riyadh", f"{base}/en/properties-for-sale-in-saudi-arabia"]
    try:  # discover more English landing pages from the sitemap, if public
        sm = _session.get(base + "/sitemap.xml", timeout=15)
        if sm.ok and "<loc>" in sm.text:
            locs = re.findall(r"<loc>(.*?)</loc>", sm.text)
            queue += [u for u in locs if "/en/" in u and re.search(r"properties-for-(sale|rent)-in|projects|auctions|faq|about", u)][:MAX_WASALT]
    except Exception as e:
        log.info("Wasalt sitemap unavailable: %s", e)
    for u in queue:
        if u in done or len(docs) >= MAX_WASALT:
            continue
        done.add(u)
        time.sleep(DELAY)
        try:
            d = _doc("Wasalt", u, fetch(u))
            if d:
                docs.append(d)
                log.info("Wasalt ✓ %s", u)
        except Blocked as e:
            log.warning("Wasalt blocked: %s", e)
        except Exception as e:
            log.warning("Wasalt skip %s: %s", u, e)
    return docs


def run(store) -> dict:
    """store(doc) persists one document. Returns a summary."""
    summary = {}
    for name, fn in (("DarGlobal", scrape_darglobal), ("Wasalt", scrape_wasalt)):
        try:
            docs = fn()
        except Exception as e:  # never crash the app because of scraping
            log.error("%s scrape failed: %s", name, e)
            docs = []
        for d in docs:
            store(d)
        summary[name] = len(docs)
    log.info("Scrape summary: %s", summary)
    return summary


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    from backend import app as appmod

    appmod.init_db()
    appmod.load_seed()
    result = run(appmod.upsert_doc)
    print("Scraped:", result)
    if "--export" in sys.argv:
        out = Path(__file__).with_name("seed_data.json")
        rows = appmod.all_docs()
        out.write_text(json.dumps([{k: r[k] for k in ("source", "title", "url", "content", "origin")} for r in rows], ensure_ascii=False, indent=1))
        print("Exported", len(rows), "docs to", out)
