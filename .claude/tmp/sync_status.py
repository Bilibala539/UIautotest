# -*- coding: utf-8 -*-
"""Sync status=verified for the 20 Wave4/5 promoted pages: frontmatter + app_map."""
import json
import re
from pathlib import Path

ROOT = Path(r"E:\UIAutotest\knowledge\swan")
PAGES = [
    "swan_搜索输入页", "swan_搜索结果页", "swan_授权门禁弹层", "swan_全国电台页",
    "swan_城市选择页", "swan_艺人页", "swan_排行榜页", "swan_我的二维码页",
    "swan_消息中心页", "swan_统一音乐库页", "swan_批量操作页", "swan_选择歌单页",
    "swan_所有角色页", "swan_角色编辑页", "swan_AI形象页", "swan_DIY形象页",
    "swan_AI平台管理页", "swan_AI历史页", "swan_视频分类页", "swan_Vision域不可达页",
]

changed = []
for name in PAGES:
    f = ROOT / "pages" / f"{name}.md"
    text = f.read_text(encoding="utf-8")
    if re.search(r"^status: draft\s*$", text, flags=re.M):
        text = re.sub(r"^status: draft\s*$", "status: verified", text, flags=re.M)
        f.write_text(text, encoding="utf-8")
        changed.append((name, "frontmatter draft->verified"))
    else:
        changed.append((name, "frontmatter: no draft status found (check)"))

mp = ROOT / "app_map.json"
data = json.loads(mp.read_text(encoding="utf-8"))
n = 0
for name in PAGES:
    entry = data["pages"].get(name)
    if entry is None:
        print(f"app_map: MISSING {name}")
        continue
    if entry.get("status") != "verified":
        entry["status"] = "verified"
        n += 1
mp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for c in changed:
    print(c)
print(f"app_map statuses updated: {n}")
