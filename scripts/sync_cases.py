"""用例定义同步(用例管理功能):把仓库里的自动化 driver 用例同步到平台 case_defs。

注(2026-10-15,用例域整合二期归一):文字用例唯一来源=平台 API/工作站创作,
本脚本原 load_text_cases(旧 KB YAML 文字用例)**已退役删除**——重跑不会再把
195 条旧 KB 文字用例灌回库。本脚本现在只负责 cases/driver/** 的 YAML 自动化
用例(POS-002)。

关联规则(平台UI设计规范 8.2 + 二期归一):
  - frontmatter `linked_case_id`(完整工作站编号)显式声明,strong;实写前经
    GET /api/case-defs 校验目标存在,未命中打 [warn] 丢弃声明回退推断
  - 无显式声明回退推断 —— 编号后缀在平台全量编号中唯一命中,weak;
    推断结果同样校验(文字用例 YAML 源已退役,路径锁定推断随之取消)
  - bug 来源: tags/标题/source 里出现的 SWAN-BUG-YYYYMMDD-NNN 编号写入 source_bug

用法:
  python scripts/sync_cases.py                       # 同步到 http://127.0.0.1:8080
  python scripts/sync_cases.py --url http://192.168.12.167:8080 --dry-run
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


def _request_json(url: str, method: str = "GET", payload: dict | None = None,
                  retries: int = 3) -> dict:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            data = None if payload is None else json.dumps(
                payload, ensure_ascii=False).encode("utf-8")
            request = urllib.request.Request(
                url, data=data,
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


def fetch_case_ids(base: str) -> set[str]:
    """平台全量用例编号(挂接目标校验用)。

    /api/case-defs 列表端点 limit 钳制 1000,全量取法改走:
    /api/case-defs/export(text 全量)+ /api/case-defs?type=auto(auto 全量)。
    """
    doc = _request_json(f"{base}/api/case-defs/export")
    ids = {str(i.get("case_id") or "").strip() for i in (doc.get("cases") or [])}
    doc = _request_json(f"{base}/api/case-defs?type=auto&limit=1000")
    ids |= {str(i.get("case_id") or "").strip() for i in (doc.get("items") or [])}
    return ids - {""}


def load_auto_cases(valid_ids: set[str]) -> tuple[list[dict], set[str]]:
    """cases/driver/** 的 YAML 整文件导入为自动化用例。

    关联锚点(二期归一): frontmatter 显式声明 > 推断 > 不挂;两级都过平台校验。
    返回 (用例列表, 显式声明命中的 case_id 集合,dry-run 据此标 [explicit])。
    """
    items: list[dict] = []
    explicit_ids: set[str] = set()
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
        # 显式映射声明: key 存在才校验(未声明静默走推断);平台中存在才采纳
        explicit_linked = ""
        fm_linked = frontmatter.get("linked_case_id")
        if fm_linked is not None:
            cand = str(fm_linked).strip()
            if cand in valid_ids:
                explicit_linked = cand
            else:
                print(f"  [warn] {rel}: frontmatter linked_case_id={fm_linked!r} "
                      f"不在平台 case_defs 中,丢弃声明回退推断")
        # 推断(兜底): 编号后缀在平台全量编号中唯一命中;歧义不挂(错挂比不挂危害大)
        haystack = " ".join(str(doc.get(k) or "") for k in ("case_id", "title", "source"))
        linked = ""
        for token in ID_TOKEN_PATTERN.findall(haystack):
            if "-" not in token:
                continue
            matches = [i for i in valid_ids if i.endswith(token)]
            if len(matches) == 1:
                linked = matches[0]
                break
        if explicit_linked:
            # 显式与推断不一致时以显式为准(推断本就弱语义),打 info 供核查
            if linked and linked != explicit_linked:
                print(f"  [info] {rel}: 显式 linked_case_id={explicit_linked} "
                      f"覆盖推断结果 {linked}")
            linked = explicit_linked
            explicit_ids.add(case_id)
        if linked and linked not in valid_ids:  # 推断结果同样过平台校验
            print(f"  [warn] {rel}: 推断 linked_case_id={linked!r} 不在平台,弃用")
            linked = ""
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
            # frontmatter 显式锚点(case_id 或 linked_case_id)= strong;纯推断 = weak
            "link_strength": "strong" if (fm_case_id or explicit_linked) else "weak",
        })
    return items, explicit_ids


def main() -> int:
    parser = argparse.ArgumentParser(description="同步自动化 driver 用例到平台")
    parser.add_argument("--url", default="http://127.0.0.1:8080")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    base = args.url.rstrip("/")

    valid_ids = fetch_case_ids(base)
    auto_cases, explicit_ids = load_auto_cases(valid_ids)
    print(f"平台编号 {len(valid_ids)} 个; 解析到自动化 driver 用例 {len(auto_cases)} 条"
          f"(显式声明映射 {len(explicit_ids)} 条)")

    if args.dry_run:
        for case in auto_cases:
            link = f" -> {case['linked_case_id']}" if case.get("linked_case_id") else ""
            if case["case_id"] in explicit_ids:
                link += " [explicit]"
            bug = f" [bug:{case['source_bug']}]" if case['source_bug'] else ""
            print(f"  [{case['case_type']} {case['link_strength']}] "
                  f"{case['case_id']}: {case['title']}{link}{bug}")
        return 0

    ok = failed = 0
    for case in auto_cases:
        try:
            _request_json(f"{base}/api/case-defs/{case['case_id']}", "PUT", case)
            ok += 1
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as error:
            failed += 1
            print(f"  [fail] {case['case_id']}: {error}")
    print(f"同步完成: 成功 {ok}, 失败 {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
