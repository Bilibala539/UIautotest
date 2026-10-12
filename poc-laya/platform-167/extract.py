"""Extract text cases from Swan platform DB for Laya POC. Read-only."""
import json, sqlite3, pathlib

DB = "file:/opt/uiautotest/output/dashboard.sqlite3?mode=ro"
OUT = pathlib.Path.home() / "laya_poc" / "cases.json"

conn = sqlite3.connect(DB, uri=True)
rows = list(conn.execute(
    "select case_id, title, content from case_defs where case_type=? order by case_id", ("text",)))

cases = []
for cid, title, content in rows:
    lines = content.splitlines()
    domain = None
    kept = []
    for ln in lines:
        if ln.startswith("domain:") and domain is None:
            domain = ln.split(":", 1)[1].strip() or None
            continue  # strip: the judge must not copy the answer
        kept.append(ln)
    cases.append({
        "case_id": cid,
        "title": title,
        "domain": domain,
        "content": "\n".join(kept).strip(),
    })

OUT.write_text(json.dumps(cases, ensure_ascii=False, indent=1), encoding="utf-8")
n_dom = sum(1 for c in cases if c["domain"])
chars = sorted(len(c["content"]) for c in cases)
print(f"cases={len(cases)} with_domain={n_dom}")
print(f"content chars p50={chars[len(chars)//2]} p95={chars[int(len(chars)*.95)]} max={chars[-1]}")
print("saved:", OUT)
