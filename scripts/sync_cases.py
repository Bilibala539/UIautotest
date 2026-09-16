"""用例定义同步(用例管理功能):把仓库里的文字用例 + 自动化脚本用例导入平台 case_defs。

关联规则(平台UI设计规范 8.2):
  - 自动化用例(cases/driver/**): YAML frontmatter 显式 `case_id` 作强锚点(link_strength=strong);
    无 frontmatter 时回退现有推断 —— source 字段里的用例编号后缀匹配文字用例,
    写入 linked_case_id(如 POS-002 -> LOGIN-L2-POS-002),并标 link_strength=weak(弱关联)
  - bug 来源: tags/标题/source 里出现的 SWAN-BUG-YYYYMMDD-NNN 编号写入 source_bug
  - 文字用例(cases/ 下除 driver 外的 **/*.yaml 的 cases: 列表逐条导入,显式 case_id,strong)

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


def _split_frontmatter(raw: str) -> tuple[dict, str]:
    """拆 YAML frontmatter(首行 --- 包裹的块)。返回 (frontmatter字典, 正文文本)。

    无 frontmatter / 解析失败时返回 ({}, 原文),调用方按现状处理。
    """
    lines = raw.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, raw
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            try:
                fm = yaml.safe_load("\n".join(lines[1:i])) or {}
            except yaml.YAMLError:
                return {}, raw  # frontmatter 坏了不硬解析,按无锚点走,不阻断同步
            return (fm if isinstance(fm, dict) else {}), "\n".join(lines[i + 1:])
    return {}, raw  # 只有开 --- 没闭合,视作无 frontmatter


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
                "link_strength": "strong",
            })
    return items


def load_auto_cases(text_cases: list[dict]) -> list[dict]:
    """cases/driver/** 的 YAML 整文件导入为自动化用例。

    锚点(规范 8.2): 优先读 frontmatter 显式 case_id(强锚点,link_strength=strong);
    无 frontmatter 时用正文 case_id,与文字用例的关联仍走"source 路径锁定 + 编号后缀
    唯一命中"推断,标 link_strength=weak,提示补锚点。
    """
    items: list[dict] = []
    for path in sorted(CASES_DIR.glob("driver/**/*.yaml")):
        rel = path.relative_to(PROJ_ROOT).as_posix()
        raw = path.read_text(encoding="utf-8")
        frontmatter, body = _split_frontmatter(raw)
        try:
            doc = yaml.safe_load(body) or {}
        except yaml.YAMLError as error:
            print(f"  [warn] YAML 解析失败 {rel}: {error}")
            continue
        if not isinstance(doc, dict):
            doc = {}
        fm_case_id = str(frontmatter.get("case_id") or "").strip()
        case_id = fm_case_id or str(doc.get("case_id") or "").strip()
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
            # frontmatter 显式锚点 = strong;回退正文/推断 = weak(提示补 case_id)
            "link_strength": "strong" if fm_case_id else "weak",
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
            strength = "" if case["case_type"] == "text" else f" [{case['link_strength']}]"
            print(f"  [{case['case_type']}{strength}] {case['case_id']}: {case['title']}{link}{bug}")
        weak = sum(1 for c in auto_cases if c.get("link_strength") == "weak")
        print(f"弱关联(auto 无 frontmatter 锚点) {weak} 条,建议在 YAML 补 case_id frontmatter")
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
