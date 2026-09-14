# -*- coding: utf-8 -*-
"""KB 双层索引体检脚本(只读)

检查 knowledge/swan 的 graph 层(backlinks.json)与 vector 层(.chroma_db/index_state.json)
是否与 pages/ 实际内容一致。用法:

    python scripts/knowledge/index_health_check.py [仓库根目录,默认向上推导]
"""
import json, hashlib, os, sys, subprocess
sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else \
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
KB = os.path.join(ROOT, "knowledge", "swan")

pages = {}
pdir = os.path.join(KB, "pages")
for f in os.listdir(pdir):
    if f.endswith(".md"):
        with open(os.path.join(pdir, f), "rb") as fh:
            pages[f[:-3]] = hashlib.md5(fh.read()).hexdigest()
print(f"[pages] 实际页面数: {len(pages)}")

# --- graph 层 ---
bl = json.load(open(os.path.join(KB, "backlinks.json"), encoding="utf-8"))
bl_map = bl.get("backlinks", {})
fwd = bl.get("forward_index", {})
fwd_pages = {os.path.basename(k)[:-3] for k in fwd if "pages" in k.replace("/", "\\")}
bl_pages = set(bl_map.keys())
print(f"[graph] stats: {bl.get('stats')}  generated_at: {bl.get('generated_at')}")
print(f"[graph] backlinks 键覆盖页面: {len(bl_pages & set(pages))}/{len(pages)}")
print(f"[graph] forward_index 覆盖页面: {len(fwd_pages & set(pages))}/{len(pages)}")
no_backlink = sorted(set(pages) - bl_pages)
print(f"[graph] 无入链(wikilink)的页面 {len(no_backlink)}: {no_backlink[:10]}{'...' if len(no_backlink) > 10 else ''}")

# --- vector 层: index_state md5 比对 ---
state = json.load(open(os.path.join(KB, ".chroma_db", "index_state.json"), encoding="utf-8"))
state_pages = {os.path.basename(k)[:-3]: v for k, v in state.items()
               if "knowledge\\swan" in k.replace("/", "\\") and k.endswith(".md") and "pages" in k}
stale = [p for p, h in state_pages.items() if pages.get(p) != h]
print(f"[vector] state 中页面: {len(state_pages)}; md5 过期: {len(stale)} {stale if stale else ''}")

# --- git 时间线(编码容错) ---
def git_log(path):
    r = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%ci %h %s", "--", path],
                       capture_output=True)
    return r.stdout.decode("utf-8", errors="replace").strip()

print(f"[git] pages/ 最后提交: {git_log('knowledge/swan/pages')}")
print(f"[git] backlinks.json 最后提交: {git_log('knowledge/swan/backlinks.json')}")
