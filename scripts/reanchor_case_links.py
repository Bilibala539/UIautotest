# -*- coding: utf-8 -*-
"""用例挂接归一执行器(用例域整合二期,2026-10-15)。

背景:REG-001~076 是上一代编号,70 条自动化用例挂接指向 REG-0NN、12 条无挂接、
POS-002 driver 挂接指向已废弃的 LOGIN-L2-POS-002。本脚本按 scripts/case_link_map.json
把挂接统一重锚到工作站编号(launch-POS-001 式),并给 REG 行写入对应工作站挂接。

用法(先干跑看差异,再实跑):
  python scripts/reanchor_case_links.py --files        # 改 py 标记 + driver YAML(仓库内,幂等)
  python scripts/reanchor_case_links.py                # 干跑:只打印 DB 将做的变更
  python scripts/reanchor_case_links.py --db           # 实写 case_defs(须在 .167 上跑;自动备份)
  python scripts/reanchor_case_links.py --db --db-path output/dashboard.sqlite3

安全设计:
  - 映射里所有目标/来源 id 实写前再校验一遍存在性,缺一即整体不写
  - --db 先备份库文件(reanchor-<时间戳>),单事务提交,失败自动回滚
  - --files 幂等,可重复跑
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import sys
import time
from pathlib import Path

PROJ_ROOT = Path(__file__).parent.parent
MAP_PATH = Path(__file__).parent / "case_link_map.json"
CASE_ID_RE = re.compile(r"^#\s*CASE-ID:\s*(\S+)\s*$", re.M)
LINKED_RE = re.compile(r"^#\s*LINKED-CASE:\s*(\S+)\s*$", re.M)
TESTS_DIR = PROJ_ROOT / "tests" / "flutter"


def load_map() -> dict:
    m = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    for key in ("reg_to_ws", "auto_relink", "auto_fill", "driver_relink",
                "marker_fixes", "marker_additions"):
        if key not in m:
            raise SystemExit(f"映射文件缺字段: {key}")
    return m


def final_links(m: dict) -> dict[str, str]:
    """case_id → 最终挂接串(逗号多值,与现行 LINKED-CASE 标记格式一致)。"""
    out: dict[str, str] = {}
    for cid, entry in m["auto_relink"].items():
        if entry["to"]:
            out[cid] = ",".join(entry["to"])
    for cid, targets in m["auto_fill"].items():
        if targets:
            out[cid] = ",".join(targets)
    for cid, entry in m["driver_relink"].items():
        if entry["to"]:
            out[cid] = ",".join(entry["to"])
    return out


# ---------------------------------------------------------------- --files

def _upsert_marker(text: str, pattern: re.Pattern, line: str) -> str:
    if pattern.search(text):
        return pattern.sub(lambda mo: line, text, count=1)
    mo = CASE_ID_RE.search(text)
    if mo:  # 已有 CASE-ID 行:LINKED-CASE 插在其后(标记两行相邻)
        nl = text.find("\n", mo.end())
        at = (nl + 1) if nl != -1 else len(text)
        return text[:at] + line + "\n" + text[at:]
    return line + "\n" + text  # 无标记行:文件头插入(标记行在 docstring 之前)


def apply_files(m: dict, dry_run: bool) -> None:
    links = final_links(m)
    fixes = m["marker_fixes"]
    adds = m["marker_additions"]
    changed = []
    for path in sorted(TESTS_DIR.glob("test_*.py")):
        text = path.read_text(encoding="utf-8")
        original = text
        mo = CASE_ID_RE.search(text)
        if path.name in adds:
            spec = adds[path.name]
            cid = spec["case_id"]
            if mo is None:  # 幂等:已有 CASE-ID 则不动
                header = f"# CASE-ID: {cid}\n# LINKED-CASE: {','.join(spec['link'])}"
                text = header + "\n" + text
        elif mo:
            cid = fixes[path.name]["case_id"] if path.name in fixes else mo.group(1)
            if mo.group(1) != cid:
                text = CASE_ID_RE.sub(f"# CASE-ID: {cid}", text, count=1)
            if cid in links:
                text = _upsert_marker(text, LINKED_RE, f"# LINKED-CASE: {links[cid]}")
        if text != original:
            changed.append(path)
            if not dry_run:
                path.write_text(text, encoding="utf-8", newline="\n")

    # POS-002 driver YAML:补 frontmatter 显式声明(sync_cases.py 的 strong 锚)
    driver_rel = PROJ_ROOT / "knowledge" / "swan" / "cases" / "driver" / "login" / "POS-002.yaml"
    if driver_rel.exists():
        raw = driver_rel.read_text(encoding="utf-8")
        if not raw.startswith("---"):
            entry = m["driver_relink"]["POS-002"]
            fm = (f"---\nlinked_case_id: {entry['to'][0]}\n---\n")
            if not dry_run:
                driver_rel.write_text(fm + raw, encoding="utf-8", newline="\n")
            changed.append(driver_rel)

    mode = "将改" if dry_run else "已改"
    print(f"[files] {mode} {len(changed)} 个文件:")
    for p in changed:
        print(f"  {p.relative_to(PROJ_ROOT)}")
    if not dry_run:
        verify_files(m)


def verify_files(m: dict) -> None:
    """改后自检:每个 CASE-ID 的 LINKED-CASE 与映射一致(冷启动两文件按各自子集单查)。"""
    links = final_links(m)
    adds = m["marker_additions"]
    bad = []
    for path in sorted(TESTS_DIR.glob("test_*.py")):
        text = path.read_text(encoding="utf-8")
        mo = CASE_ID_RE.search(text)
        if not mo:
            continue
        cid = mo.group(1)
        ml = LINKED_RE.search(text)
        if path.name in adds:
            want = ",".join(adds[path.name]["link"])
            if cid != adds[path.name]["case_id"] or not ml or ml.group(1) != want:
                bad.append(f"{path.name}: 期望 {cid} -> {want}")
        elif cid in links and (not ml or ml.group(1) != links[cid]):
            bad.append(f"{path.name}: {cid} 标记={ml.group(1) if ml else '无'} 期望={links[cid]}")
    fm = (PROJ_ROOT / "knowledge" / "swan" / "cases" / "driver" / "login" / "POS-002.yaml").read_text(encoding="utf-8")
    if not fm.startswith("---\nlinked_case_id:"):
        bad.append("POS-002.yaml: frontmatter 未写入")
    print(f"[verify] {'全部一致' if not bad else chr(10).join(bad)}")


# ---------------------------------------------------------------- --db

def apply_db(m: dict, db_path: str, dry_run: bool) -> None:
    links = final_links(m)
    reg_map = {k: ",".join(v) for k, v in m["reg_to_ws"].items() if v}

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA busy_timeout=5000")
    all_ids = {r[0] for r in conn.execute("SELECT case_id FROM case_defs")}

    # 实写前全量校验(映射文件可能晚于库变化)
    missing = [cid for cid in list(links) + list(reg_map) if cid not in all_ids]
    bad_targets = sorted({t for v in list(links.values()) + list(reg_map.values())
                          for t in v.split(",") if t not in all_ids})
    if missing or bad_targets:
        conn.close()
        raise SystemExit(f"[db] 校验失败,未写库: 缺行={missing} 目标不存在={bad_targets}")

    updates = [(links[cid], cid) for cid in sorted(links)]
    updates += [(reg_map[cid], cid) for cid in sorted(reg_map)]
    print(f"[db] {'将执行' if dry_run else '执行'} {len(updates)} 条 UPDATE:")
    for link, cid in updates[:8]:
        print(f"  {cid}: -> {link}")
    if len(updates) > 8:
        print(f"  ... 其余 {len(updates) - 8} 条见 case_link_map.json")

    if dry_run:
        conn.close()
        return

    backup = f"{db_path}.bak-reanchor-{time.strftime('%Y%m%d-%H%M%S')}"
    conn.close()  # 备份须在写连接打开前完成(WAL 下文件级备份需一致性)
    shutil.copy2(db_path, backup)
    print(f"[db] 已备份: {backup}")

    conn = sqlite3.connect(db_path, isolation_level=None)
    conn.execute("PRAGMA busy_timeout=5000")
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.executemany(
            "UPDATE case_defs SET linked_case_id=? WHERE case_id=?", updates)
        row = conn.execute(
            "SELECT COUNT(*) FROM case_defs WHERE case_type='auto' "
            "AND linked_case_id LIKE 'REG-%'").fetchone()[0]
        if row:
            raise RuntimeError(f"仍有 {row} 条 auto 挂着 REG-*,回滚")
        conn.execute("COMMIT")
    except Exception as error:
        conn.execute("ROLLBACK")
        raise SystemExit(f"[db] 失败已回滚: {error}") from error

    done = conn.execute(
        "SELECT COUNT(*) FROM case_defs WHERE linked_case_id LIKE '%POS-%' "
        "OR linked_case_id LIKE '%NEG-%'").fetchone()[0]
    conn.close()
    print(f"[db] 提交完成;挂接含工作站编号的行共 {done} 条")


def main() -> int:
    parser = argparse.ArgumentParser(description="用例挂接归一(REG→工作站编号重锚)")
    parser.add_argument("--files", action="store_true", help="更新 py 标记与 driver YAML")
    parser.add_argument("--db", action="store_true", help="写 case_defs(须在 .167 上跑)")
    parser.add_argument("--db-path", default="/opt/uiautotest/output/dashboard.sqlite3")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    m = load_map()
    print(f"[map] reg_to_ws={len(m['reg_to_ws'])} auto_relink={len(m['auto_relink'])} "
          f"auto_fill={len(m['auto_fill'])} driver={len(m['driver_relink'])} "
          f"marker_fixes={len(m['marker_fixes'])} marker_additions={len(m['marker_additions'])}")
    if args.files:
        apply_files(m, dry_run=False)
    if args.db:
        apply_db(m, args.db_path, dry_run=False)
    if not args.files and not args.db:
        apply_db(m, args.db_path, dry_run=True)  # 缺省=干跑,只打印 DB 将做的变更
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
