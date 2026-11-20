"""Runs the 8 assignment questions against a running instance and saves test_results.md.
Usage: python scripts/test_questions.py https://your-app.onrender.com
"""
import json, sys, time, urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000").rstrip("/")
QS = [
    "What is DarGlobal?",
    "What projects are listed on DarGlobal?",
    "What information does Wasalt provide?",
    "Tell me about properties listed on Wasalt.",
    "Compare the information available from DarGlobal and Wasalt.",
    "What amenities are mentioned in the collected project data?",
    "What is the price of a particular project, if publicly available?",
    "Tell me something that is not available in the scraped dataset: what is the current mortgage rate in Spain?",
]

def post(q):
    req = urllib.request.Request(BASE + "/api/chat", data=json.dumps({"message": q}).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)

print("health:", urllib.request.urlopen(BASE + "/health", timeout=30).read().decode()[:300])
out = [f"# Test results for {BASE}\n"]
for i, q in enumerate(QS, 1):
    for attempt in range(4):
        try:
            d = post(q); break
        except Exception as e:
            d = {"answer": f"ERROR: {e}", "sources": [], "model": "-"}; time.sleep(20)
    srcs = ", ".join(sorted({s["source"] for s in d["sources"]})) or "none"
    print(f"\n[{i}] {q}\n    sources: {srcs} | model: {d.get('model')}\n    {d['answer'][:300]!r}")
    out.append(f"## {i}. {q}\n**Model:** {d.get('model')}  \n**Sources:** {srcs}\n\n{d['answer']}\n\n" + "\n".join(f"- [{s['source']}] {s['title']} — {s['url']}" for s in d["sources"]) + "\n")
    time.sleep(8)  # be gentle with free-tier rate limits
open("test_results.md", "w", encoding="utf-8").write("\n".join(out))
print("\nSaved test_results.md")
