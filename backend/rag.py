"""Lightweight local retrieval: passage chunking + BM25 ranking with source-aware routing.

No external embedding API is needed, so retrieval is free, fast and works offline.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

STOP = set("""a an the and or of to in on for with at by from is are was were be been being it its this that these those
what which who whom whose how when where why do does did can could should would will about tell me show give list any all
some there their them they you your i we our us as if than then so such not no yes also more most info information
please explain describe provide find get have has had""".split())

SOURCE_ALIASES = {
    "DarGlobal": ("darglobal", "dar global", "dar-global"),
    "Wasalt": ("wasalt", "وصلت"),
}
OVERVIEW_URLS = {"https://darglobal.co.uk", "https://wasalt.sa/en", "https://wasalt.sa/en/corporate"}
GENERIC_RE = re.compile(r"\b(what is|what's|who is|who are|about|overview|introduce|describe)\b")
COMPARE_WORDS = ("compare", "comparison", "versus", " vs ", " vs.", "difference", "both", "differ", "contrast")


def tokenize(text: str) -> list[str]:
    out = []
    for w in re.findall(r"[a-z0-9\u0600-\u06ff]+", text.lower()):
        if len(w) < 2 or w in STOP:
            continue
        if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        out.append(w)
    return out


def chunk_text(text: str, size: int = 900) -> list[str]:
    parts = [p.strip() for p in re.split(r"\n+", text) if p.strip()]
    chunks, cur = [], ""
    for p in parts:
        while len(p) > size * 1.4:  # very long line: split on sentence boundary
            cut = p.rfind(". ", 0, size)
            cut = cut + 1 if cut > 200 else size
            if cur:
                chunks.append(cur)
                cur = ""
            chunks.append(p[:cut].strip())
            p = p[cut:].strip()
        if len(cur) + len(p) + 1 > size and cur:
            chunks.append(cur)
            cur = p
        else:
            cur = f"{cur}\n{p}".strip()
    if cur:
        chunks.append(cur)
    return chunks


@dataclass
class Chunk:
    doc_id: int
    source: str
    title: str
    url: str
    text: str
    tf: Counter
    length: int


class Index:
    def __init__(self) -> None:
        self.chunks: list[Chunk] = []
        self.df: Counter = Counter()
        self.avg_len = 1.0

    def build(self, docs: list[dict]) -> None:
        self.chunks, self.df = [], Counter()
        for d in docs:
            for piece in chunk_text(d["content"]):
                toks = tokenize(d["title"] + " " + d["title"] + " " + piece)  # title counts double
                tf = Counter(toks)
                self.chunks.append(Chunk(d["id"], d["source"], d["title"], d["url"], piece, tf, max(1, len(toks))))
                for t in tf:
                    self.df[t] += 1
        self.avg_len = (sum(c.length for c in self.chunks) / len(self.chunks)) if self.chunks else 1.0

    def _bm25(self, q: list[str], c: Chunk, k1: float = 1.5, b: float = 0.75) -> float:
        n = len(self.chunks)
        score = 0.0
        for t in set(q):
            f = c.tf.get(t, 0)
            if not f:
                continue
            idf = math.log(1 + (n - self.df[t] + 0.5) / (self.df[t] + 0.5))
            score += idf * f * (k1 + 1) / (f + k1 * (1 - b + b * c.length / self.avg_len))
        return score

    @staticmethod
    def detect_sources(query: str) -> set[str]:
        ql = f" {query.lower()} "
        found = {s for s, al in SOURCE_ALIASES.items() if any(a in ql for a in al)}
        if any(w in ql for w in COMPARE_WORDS):
            found = {"DarGlobal", "Wasalt"}
        return found

    def search(self, query: str, k: int = 6, prev_user: str | None = None) -> list[tuple[float, Chunk]]:
        q = tokenize(query)
        if prev_user and len(q) <= 4:  # short follow-up: borrow context from the previous question
            q = q + tokenize(prev_user)
        if not q or not self.chunks:
            return []
        generic = bool(GENERIC_RE.search(query.lower())) and len(tokenize(query)) <= 4
        wanted = self.detect_sources(query + " " + (prev_user or "" if len(tokenize(query)) <= 4 else ""))
        scored = []
        for c in self.chunks:
            s = self._bm25(q, c)
            if s <= 0:
                continue
            if wanted and c.source not in wanted:
                s *= 0.25
            if generic and c.url.rstrip("/") in OVERVIEW_URLS:
                s *= 3.0  # "What is X?" should be answered from the company overview page
            scored.append((s, c))
        scored.sort(key=lambda x: x[0], reverse=True)
        if not scored:
            return []
        top = scored[0][0]
        scored = [x for x in scored if x[0] >= top * 0.18]
        # when comparing / both sources named, guarantee each source is represented
        if len(wanted) > 1:
            picked, per = [], {s: 0 for s in wanted}
            for s, c in scored:
                if c.source in per and per[c.source] < k // len(wanted):
                    picked.append((s, c))
                    per[c.source] += 1
            for s, c in scored:
                if len(picked) >= k:
                    break
                if (s, c) not in picked:
                    picked.append((s, c))
            return sorted(picked, key=lambda x: x[0], reverse=True)[:k]
        return scored[:k]
