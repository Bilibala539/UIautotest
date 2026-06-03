"""
知识库健康度检查

静态扫描知识库，检测以下问题：
1. 断链：[[link]] 指向不存在的页面
2. 孤岛页面：没有任何 transition 连入/连出的页面
3. 缺失章节：pages/*.md 缺少必须段落
4. 无文档页面：app_map 中注册但无 .md 文件的页面
5. 过时标记：draft/ 中长期未转正的草稿
6. 空反向引用：没有任何页面引用的页面（可能是孤立的）
7. transition 断裂：transition 引用了不存在的 page_id

用法:
  python scripts/knowledge/health_check.py           # 完整检查
  python scripts/knowledge/health_check.py --json    # 输出 JSON 格式
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

PROJ_ROOT = Path(__file__).parent.parent.parent
KNOWLEDGE_DIR = PROJ_ROOT / "explorer_output" / "knowledge"
PAGES_DIR = KNOWLEDGE_DIR / "pages"
DRAFT_DIR = KNOWLEDGE_DIR / "draft"
APP_MAP_PATH = KNOWLEDGE_DIR / "app_map.json"
BACKLINKS_PATH = KNOWLEDGE_DIR / "backlinks.json"
AUDIT_STATE_PATH = KNOWLEDGE_DIR / "audit_state.json"

REQUIRED_SECTIONS = ["## 页面概述", "## 进入方式", "## 关键元素"]
RECOMMENDED_SECTIONS = ["## 关联", "## 页面布局"]
LINK_PATTERN = re.compile(r'\[\[([^\]]+)\]\]')
FRONTMATTER_PATTERN = re.compile(r'^---\n(.*?)\n---\n', re.DOTALL)


def _parse_frontmatter_aliases(content: str) -> tuple:
    """从 YAML frontmatter 提取 (page_id, [aliases])。"""
    m = FRONTMATTER_PATTERN.match(content)
    if not m:
        return None, []
    body = m.group(1)
    page_id = None
    aliases = []
    cur_key = None
    for line in body.split('\n'):
        s = line.rstrip()
        if not s:
            continue
        if line.startswith('  - ') and cur_key == 'aliases':
            aliases.append(line[4:].strip().strip('"\''))
            continue
        if ':' in s and not s.startswith(' '):
            k, _, v = s.partition(':')
            k = k.strip()
            v = v.strip()
            cur_key = k
            if k == 'page_id' and v:
                page_id = v.strip('"\'')
            elif k == 'aliases':
                if v.startswith('[') and v.endswith(']'):
                    aliases = [x.strip().strip('"\'') for x in v[1:-1].split(',') if x.strip()]
    return page_id, aliases


def _build_known_targets() -> set:
    """已知 link 目标集合：app_map page_id + pages/draft 文件 stem + frontmatter aliases。"""
    app_map = load_app_map()
    known = set(app_map.get("pages", {}).keys())
    for d in (PAGES_DIR, DRAFT_DIR):
        if not d.exists():
            continue
        for f in d.glob("*.md"):
            known.add(f.stem)
            try:
                content = f.read_text(encoding="utf-8")
            except Exception:
                continue
            pid, aliases = _parse_frontmatter_aliases(content)
            if pid:
                known.add(pid)
            known.update(aliases)
    return known

# 巡检时间衰减配置
AUDIT_FRESHNESS_DAYS = {
    "fresh": 7,       # 7天内巡检过 = 新鲜
    "normal": 14,     # 14天内 = 正常
    "stale": 30,      # 30天内 = 变旧
    "expired": 30,    # 超过30天 = 过期
}


def load_app_map():
    if APP_MAP_PATH.exists():
        return json.loads(APP_MAP_PATH.read_text(encoding="utf-8-sig"))
    return {"pages": {}, "transitions": []}


def check_broken_links() -> list:
    """检查所有 [[link]] 是否指向存在的页面（含 frontmatter aliases）"""
    issues = []
    known_pages = _build_known_targets()

    for md_file in PAGES_DIR.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        # 排除 backlinks 段
        content_clean = re.sub(
            r'<!-- backlinks:start -->.*?<!-- backlinks:end -->',
            '', content, flags=re.DOTALL
        )
        links = LINK_PATTERN.findall(content_clean)
        for link in links:
            if link not in known_pages:
                issues.append({
                    "type": "broken_link",
                    "severity": "warning",
                    "file": str(md_file.relative_to(KNOWLEDGE_DIR)),
                    "detail": f"[[{link}]] 指向不存在的页面",
                })
    return issues


def check_orphan_pages() -> list:
    """检查孤岛页面：在 transitions 中没有任何连入或连出"""
    issues = []
    app_map = load_app_map()
    transitions = app_map.get("transitions", [])
    pages = set(app_map.get("pages", {}).keys())

    connected = set()
    for t in transitions:
        connected.add(t["from"])
        connected.add(t["to"])

    orphans = pages - connected
    for p in orphans:
        issues.append({
            "type": "orphan_page",
            "severity": "info",
            "page_id": p,
            "detail": f"页面 '{p}' 在导航图谱中无任何 transition 连接",
        })
    return issues


def check_missing_sections() -> list:
    """检查 pages/*.md 缺少必须/推荐章节"""
    issues = []
    for md_file in PAGES_DIR.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        rel_path = str(md_file.relative_to(KNOWLEDGE_DIR))

        for section in REQUIRED_SECTIONS:
            if section not in content:
                issues.append({
                    "type": "missing_required_section",
                    "severity": "error",
                    "file": rel_path,
                    "detail": f"缺少必须章节: {section}",
                })

        for section in RECOMMENDED_SECTIONS:
            if section not in content:
                issues.append({
                    "type": "missing_recommended_section",
                    "severity": "info",
                    "file": rel_path,
                    "detail": f"缺少推荐章节: {section}",
                })
    return issues


def check_undocumented_pages() -> list:
    """检查 app_map 中注册但无 .md 文件的页面"""
    issues = []
    app_map = load_app_map()
    existing_files = {f.stem for f in PAGES_DIR.glob("*.md")}

    for pid, info in app_map.get("pages", {}).items():
        detail_path = info.get("detail")
        if detail_path:
            full_path = KNOWLEDGE_DIR / detail_path
            if not full_path.exists():
                issues.append({
                    "type": "undocumented_page",
                    "severity": "warning",
                    "page_id": pid,
                    "detail": f"app_map 引用了 '{detail_path}' 但文件不存在",
                })
        elif pid not in existing_files:
            issues.append({
                "type": "undocumented_page",
                "severity": "info",
                "page_id": pid,
                "detail": f"页面 '{info.get('name', pid)}' 无详细文档（detail=null）",
            })
    return issues


def check_stale_drafts() -> list:
    """检查 draft/ 中的文件"""
    issues = []
    if not DRAFT_DIR.exists():
        return issues

    for md_file in DRAFT_DIR.glob("*.md"):
        if md_file.name == ".gitkeep":
            continue
        content = md_file.read_text(encoding="utf-8")
        is_unverified = "<!-- status: unverified -->" in content
        issues.append({
            "type": "stale_draft",
            "severity": "warning" if is_unverified else "info",
            "file": f"draft/{md_file.name}",
            "detail": f"草稿未转正{'（验证失败）' if is_unverified else '（待验证）'}",
        })
    return issues


def check_transition_integrity() -> list:
    """检查 transitions 引用的 page_id 是否都在 pages 中注册"""
    issues = []
    app_map = load_app_map()
    pages = set(app_map.get("pages", {}).keys())

    for i, t in enumerate(app_map.get("transitions", [])):
        for field in ["from", "to"]:
            if t[field] not in pages:
                issues.append({
                    "type": "transition_broken",
                    "severity": "error",
                    "detail": f"transition[{i}].{field}='{t[field]}' 不在 pages 中",
                })

        # 检查是否有 type 字段
        if "type" not in t:
            issues.append({
                "type": "transition_no_type",
                "severity": "info",
                "detail": f"transition[{i}] ({t['from']}→{t['to']}) 缺少 type 字段",
            })
    return issues


def check_unreferenced_pages() -> list:
    """检查没有被任何页面 [[link]] 引用的页面"""
    issues = []
    if not BACKLINKS_PATH.exists():
        return issues

    bl_data = json.loads(BACKLINKS_PATH.read_text(encoding="utf-8"))
    backlinks = bl_data.get("backlinks", {})
    app_map = load_app_map()

    for pid in app_map.get("pages", {}).keys():
        if pid not in backlinks and pid != "message_page":  # 首页不需要被引用
            issues.append({
                "type": "unreferenced_page",
                "severity": "info",
                "page_id": pid,
                "detail": f"页面 '{pid}' 没有被任何其他页面的 [[link]] 引用",
            })
    return issues


def check_audit_freshness() -> list:
    """检查巡检新鲜度：距上次 audit-kb 越久，问题越严重"""
    issues = []

    if not AUDIT_STATE_PATH.exists():
        # 从未巡检过
        app_map = load_app_map()
        for pid in app_map.get("pages", {}).keys():
            issues.append({
                "type": "never_audited",
                "severity": "warning",
                "page_id": pid,
                "detail": f"页面 '{pid}' 从未被 audit-kb 巡检验证过",
                "days_since_audit": None,
            })
        return issues

    audit_state = json.loads(AUDIT_STATE_PATH.read_text(encoding="utf-8"))
    app_map = load_app_map()
    now = datetime.now()

    for pid in app_map.get("pages", {}).keys():
        page_audit = audit_state.get("pages", {}).get(pid)

        if not page_audit:
            issues.append({
                "type": "never_audited",
                "severity": "warning",
                "page_id": pid,
                "detail": f"页面 '{pid}' 从未被巡检",
                "days_since_audit": None,
            })
            continue

        last_audit_str = page_audit.get("last_audited")
        if not last_audit_str:
            issues.append({
                "type": "never_audited",
                "severity": "warning",
                "page_id": pid,
                "detail": f"页面 '{pid}' 无巡检时间记录",
                "days_since_audit": None,
            })
            continue

        last_audit = datetime.fromisoformat(last_audit_str)
        days_ago = (now - last_audit).days
        last_result = page_audit.get("result", "unknown")

        if days_ago <= AUDIT_FRESHNESS_DAYS["fresh"]:
            # 新鲜，不扣分
            continue
        elif days_ago <= AUDIT_FRESHNESS_DAYS["normal"]:
            issues.append({
                "type": "audit_aging",
                "severity": "info",
                "page_id": pid,
                "detail": f"页面 '{pid}' 上次巡检在 {days_ago} 天前（正常范围，结果: {last_result}）",
                "days_since_audit": days_ago,
            })
        elif days_ago <= AUDIT_FRESHNESS_DAYS["stale"]:
            issues.append({
                "type": "audit_stale",
                "severity": "warning",
                "page_id": pid,
                "detail": f"页面 '{pid}' 上次巡检在 {days_ago} 天前（建议重新巡检，结果: {last_result}）",
                "days_since_audit": days_ago,
            })
        else:
            issues.append({
                "type": "audit_expired",
                "severity": "error",
                "page_id": pid,
                "detail": f"页面 '{pid}' 上次巡检在 {days_ago} 天前（已过期，内容可信度低，结果: {last_result}）",
                "days_since_audit": days_ago,
            })

    return issues


def compute_health_score(issues: list) -> dict:
    """计算健康度评分（含巡检衰减）"""
    error_count = sum(1 for i in issues if i["severity"] == "error")
    warning_count = sum(1 for i in issues if i["severity"] == "warning")
    info_count = sum(1 for i in issues if i["severity"] == "info")

    # 基础分：满分100，按问题扣分
    base_score = max(0, 100 - error_count * 10 - warning_count * 3 - info_count * 1)

    # 巡检新鲜度加分：有通过巡检记录的页面给予奖励
    freshness_bonus = 0
    if AUDIT_STATE_PATH.exists():
        audit_state = json.loads(AUDIT_STATE_PATH.read_text(encoding="utf-8"))
        app_map = load_app_map()
        total_pages = len(app_map.get("pages", {}))
        now = datetime.now()

        verified_recent = 0
        for pid, page_audit in audit_state.get("pages", {}).items():
            last_str = page_audit.get("last_audited")
            if not last_str:
                continue
            days_ago = (now - datetime.fromisoformat(last_str)).days
            if days_ago <= AUDIT_FRESHNESS_DAYS["normal"] and page_audit.get("result") == "passed":
                verified_recent += 1

        if total_pages > 0:
            freshness_bonus = int(20 * verified_recent / total_pages)

    score = min(100, base_score + freshness_bonus)

    if score >= 90:
        grade = "A"
    elif score >= 75:
        grade = "B"
    elif score >= 60:
        grade = "C"
    elif score >= 40:
        grade = "D"
    else:
        grade = "F"

    return {
        "score": score,
        "grade": grade,
        "base_score": base_score,
        "freshness_bonus": freshness_bonus,
        "errors": error_count,
        "warnings": warning_count,
        "info": info_count,
        "total_issues": len(issues),
    }


def compute_coverage_stats() -> dict:
    """计算知识库覆盖率统计"""
    app_map = load_app_map()
    total_pages = len(app_map.get("pages", {}))
    documented_pages = sum(
        1 for info in app_map.get("pages", {}).values()
        if info.get("detail") and (KNOWLEDGE_DIR / info["detail"]).exists()
    )
    total_transitions = len(app_map.get("transitions", []))
    typed_transitions = sum(
        1 for t in app_map.get("transitions", []) if "type" in t
    )

    page_files = list(PAGES_DIR.glob("*.md"))
    pages_with_relations = 0
    for f in page_files:
        content = f.read_text(encoding="utf-8")
        if "## 关联" in content:
            pages_with_relations += 1

    return {
        "total_pages_registered": total_pages,
        "pages_with_docs": documented_pages,
        "pages_doc_coverage": f"{documented_pages}/{total_pages} ({100*documented_pages//max(total_pages,1)}%)",
        "total_transitions": total_transitions,
        "transitions_with_type": f"{typed_transitions}/{total_transitions}",
        "page_files_count": len(page_files),
        "pages_with_relations": f"{pages_with_relations}/{len(page_files)}",
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="知识库健康度检查")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    # 运行所有检查
    all_issues = []
    all_issues.extend(check_broken_links())
    all_issues.extend(check_orphan_pages())
    all_issues.extend(check_missing_sections())
    all_issues.extend(check_undocumented_pages())
    all_issues.extend(check_stale_drafts())
    all_issues.extend(check_transition_integrity())
    all_issues.extend(check_unreferenced_pages())
    all_issues.extend(check_audit_freshness())

    health = compute_health_score(all_issues)
    coverage = compute_coverage_stats()

    if args.json:
        output = {
            "checked_at": datetime.now().isoformat(),
            "health": health,
            "coverage": coverage,
            "issues": all_issues,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    # 人类可读输出
    print("=" * 60)
    print(f"📊 知识库健康度报告")
    print(f"   检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    print(f"\n🏥 健康评分: {health['score']}/100 (等级: {health['grade']})")
    print(f"   基础分: {health['base_score']}  巡检加分: +{health['freshness_bonus']}")
    print(f"   ❌ 错误: {health['errors']}  ⚠️ 警告: {health['warnings']}  ℹ️ 信息: {health['info']}")

    print(f"\n📈 覆盖率统计:")
    print(f"   页面文档覆盖: {coverage['pages_doc_coverage']}")
    print(f"   Transitions 有 type: {coverage['transitions_with_type']}")
    print(f"   页面有关联段: {coverage['pages_with_relations']}")
    print(f"   页面文件总数: {coverage['page_files_count']}")

    if all_issues:
        print(f"\n{'─' * 60}")
        print(f"📋 问题清单 (共 {len(all_issues)} 项)")
        print(f"{'─' * 60}")

        # 按严重度分组
        for severity, emoji in [("error", "❌"), ("warning", "⚠️"), ("info", "ℹ️")]:
            items = [i for i in all_issues if i["severity"] == severity]
            if items:
                print(f"\n{emoji} {severity.upper()} ({len(items)})")
                for item in items:
                    loc = item.get("file") or item.get("page_id") or ""
                    print(f"   [{item['type']}] {loc}: {item['detail']}")

    print(f"\n{'=' * 60}")
    if health['grade'] in ('A', 'B'):
        print("✅ 知识库状态良好")
    elif health['grade'] == 'C':
        print("⚠️ 知识库有一些问题需要关注")
    else:
        print("❌ 知识库需要维护")


if __name__ == "__main__":
    main()
