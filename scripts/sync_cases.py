"""用例定义同步(用例管理功能):把仓库里的文字用例 + 自动化脚本用例导入平台 case_defs。

关联规则:
  - 自动化用例(cases/driver/**): source 字段里出现的用例编号后缀匹配文字用例,
    写入 linked_case_id(如 POS-002 -> LOGIN-L2-POS-002)
  - bug 来源: tags/标题/source 里出现的 SWAN-BUG-YYYYMMDD-NNN 编号写入 source_bug
  - 文字用例(cases/ 下除 driver 外的 **/*.yaml 的 cases: 列表逐条导入)

用法:
  python scripts/sync_cases.py                       # 同步到 http://127.0.0.1:8080
  python scripts/sync_cases.py --url http://192.168.12.166:8080 --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

PROJ_ROOT = Path(__file__).parent.parent
CASES_DIR = PROJ_ROOT / "knowledge" / "swan" / "cases"
BUG_PATTERN = re.compile(r"SWAN-BUG-\d{8}-\d+")
ID_TOKEN_PATTERN = re.compile(r"\b[A-Z0-9]+(?:-[A-Z0-9]+)*\b")
DRIVER_PREFIX = "knowledge/swan/cases/driver/"


def _post_or_put(url: str, method: str, payload: dict, retries: int = 3) -> dict:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(
                url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json"}, method=method,
            )
            with urllib.request.urlopen(request, timeout=15) as response:
                return json.loads(response.read().decode("utf-8"))
        except OSError as error:  # 端口瞬时耗尽等可重试错误
            last_error = error
            time.sleep(0.5 * (attempt + 1))
    raise last_error


def load_text_cases() -> list[dict]:
    """cases/ 下除 driver 外的 YAML,逐条 cases: 列表导入为文字用例。"""
    items: list[dict] = []
    for path in sorted(CASES_DIR.glob("**/*.yaml")):
        rel = path.relative_to(PROJ_ROOT).as_posix()
        if rel.startswith(DRIVER_PREFIX):
            continue
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as error:
            print(f"  [warn] YAML 解析失败 {rel}: {error}")
            continue
        file_module = str(doc.get("module") or "").split("(")[0].strip()
        level = doc.get("level")
        level = level[0] if isinstance(level, list) and level else str(level or "")
        for entry in doc.get("cases") or []:
            case_id = str(entry.get("case_id") or "").strip()
            if not case_id:
                continue
            tags = entry.get("tags") or []
            if not isinstance(tags, list):
                tags = [str(tags)]
            tags_text = " ".join(str(t) for t in tags)
            bugs = sorted(set(BUG_PATTERN.findall(
                f"{case_id} {entry.get('name') or ''} {tags_text}")))
            items.append({
                "case_id": case_id,
                "case_type": "text",
                "title": str(entry.get("name") or case_id).strip(),
                "module": file_module,
                "priority": str(entry.get("priority") or level).strip(),
                "source": rel,
                "source_bug": bugs[0] if bugs else "",
                "file_path": rel,
                "content": yaml.dump(entry, allow_unicode=True, sort_keys=False),
            })
    return items


def load_auto_cases(text_cases: list[dict]) -> list[dict]:
    """cases/driver/** 的 YAML 整文件导入为自动化用例,后缀匹配挂文字用例。"""
    items: list[dict] = []
    for path in sorted(CASES_DIR.glob("driver/**/*.yaml")):
        rel = path.relative_to(PROJ_ROOT).as_posix()
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as error:
            print(f"  [warn] YAML 解析失败 {rel}: {error}")
            continue
        case_id = str(doc.get("case_id") or "").strip()
        if not case_id:
            continue
        # 关联文字用例: source 里的 YAML 路径锁定来源文件,再用编号后缀匹配;
        # 无路径时全量后缀匹配(唯一命中才挂,避免歧义)
        haystack = " ".join(str(doc.get(k) or "") for k in ("case_id", "title", "source"))
        linked = ""
        path_match = re.search(r"knowledge/[\w/.\-]+\.yaml", haystack)
        candidates = [c for c in text_cases]
        if path_match:
            candidates = [c for c in text_cases
                          if c["file_path"].endswith(path_match.group(0))]
        for token in ID_TOKEN_PATTERN.findall(haystack):
            if "-" not in token:
                continue
            matches = [c["case_id"] for c in candidates
                       if c["case_id"].endswith(token)]
            if len(matches) == 1:
                linked = matches[0]
                break
        raw = path.read_text(encoding="utf-8")
        bugs = sorted(set(BUG_PATTERN.findall(
            f"{doc.get('title') or ''} {doc.get('source') or ''} {raw[:2000]}")))
        items.append({
            "case_id": case_id,
            "case_type": "auto",
            "title": str(doc.get("title") or case_id).strip(),
            "module": str(doc.get("module") or "").strip(),
            "priority": str(doc.get("priority") or "").strip(),
            "source": str(doc.get("source") or "").strip(),
            "source_bug": bugs[0] if bugs else "",
            "file_path": rel,
            "content": raw,
            "linked_case_id": linked,
        })
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description="同步用例定义到平台")
    parser.add_argument("--url", default="http://127.0.0.1:8080")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    base = args.url.rstrip("/")

    text_cases = load_text_cases()
    auto_cases = load_auto_cases(text_cases)
    print(f"解析到 文字用例 {len(text_cases)} 条, 自动化用例 {len(auto_cases)} 条")

    if args.dry_run:
        for case in text_cases + auto_cases:
            link = f" -> {case['linked_case_id']}" if case.get("linked_case_id") else ""
            bug = f" [bug:{case['source_bug']}]" if case.get("source_bug") else ""
            print(f"  [{case['case_type']}] {case['case_id']}: {case['title']}{link}{bug}")
        return 0

    ok = failed = 0
    for case in text_cases + auto_cases:
        try:
            _post_or_put(f"{base}/api/case-defs/{case['case_id']}", "PUT", case)
            ok += 1
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as error:
            failed += 1
            print(f"  [fail] {case['case_id']}: {error}")
    print(f"同步完成: 成功 {ok}, 失败 {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
