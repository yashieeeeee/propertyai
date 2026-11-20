import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from backend.rag import Index

docs = [dict(id=i, **d) for i, d in enumerate(json.loads((pathlib.Path(__file__).resolve().parents[1] / "backend/seed_data.json").read_text()))]
idx = Index(); idx.build(docs)

def top(q, prev=None, k=6):
    return [(round(s, 1), c.source, c.title) for s, c in idx.search(q, k=k, prev_user=prev)]

def test_both_sources_present():
    assert {d["source"] for d in docs} == {"DarGlobal", "Wasalt"}

def test_darglobal_what_is():
    assert top("What is DarGlobal?")[0][1] == "DarGlobal"

def test_wasalt_info():
    assert top("What information does Wasalt provide?")[0][1] == "Wasalt"

def test_compare_has_both():
    assert {s for _, s, _ in top("Compare the information available from DarGlobal and Wasalt")} == {"DarGlobal", "Wasalt"}

def test_amenities():
    t = top("What amenities are mentioned in the project data?")
    assert any("Astera" in x[2] or "Trump" in x[2] for x in t)

def test_location_saudi():
    assert any("Saudi" in x[2] or "Jeddah" in x[2] for x in top("Find properties in Jeddah"))

def test_followup_uses_previous():
    t = top("what about its amenities?", prev="Tell me about The Astera by Aston Martin")
    assert "Astera" in t[0][2]

def test_nonsense_empty():
    assert top("zzzxqv blorptang") == []

def test_what_is_uses_overview_page():
    for q, url in (("What is DarGlobal?", "https://darglobal.co.uk/"), ("What is Wasalt?", "https://wasalt.sa/en")):
        res = idx.search(q, k=3)
        assert res[0][1].url.rstrip("/") == url.rstrip("/"), (q, res[0][1].url)
