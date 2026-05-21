"""
知识库草稿转正脚本

流程:
  1. explorer 写新发现到 draft/ 目录
  2. 本脚本验证草稿质量（结构完整性 + 链接有效性）
  3. 验证通过 → 移入 pages/ + 更新 app_map.json + 触发 re-embed
  4. 验证失败 → 保留在 draft/ 标记 unverified

用法:
  python scripts/knowledge/promote_knowledge.py                    # 验证并转正所有草稿
  python scripts/knowledge/promote_knowledge.py --check-only       # 只验证不转正
  python scripts/knowledge/promote_knowledge.py --file draft/x.md  # 指定文件
"""

import os
import re
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime

KNOWLEDGE_DIR = Path("explorer_output/knowledge")
DRAFT_DIR = KNOWLEDGE_DIR / "draft"
PAGES_DIR = KNOWLEDGE_DIR / "pages"
APP_MAP_PATH = KNOWLEDGE_DIR / "app_map.json"

REQUIRED_SECTIONS = ["## 页面概述", "## 进入方式", "## 关键元素"]
LINK_PATTERN = re.compile(r'\[\[(\w+)\]\]')


def validate_draft(filepath: Path) -> dict:
    """验证草稿文档质量，返回验证结果"""
    result = {
        "file": str(filepath),
        "passed": True,
        "errors": [],
        "warnings": [],
        "links": [],
    }

    content = filepath.read_text(encoding="utf-8")

    # 检查标题
    if not content.startswith("# "):
        result["errors"].append("缺少一级标题")
        result["passed"] = False

    # 检查必要章节
    for section in REQUIRED_SECTIONS:
        if section not in content:
            result["warnings"].append(f"缺少章节: {section}")

    # 检查链接有效性
    links = LINK_PATTERN.findall(content)
    result["links"] = links
    for link in links:
        target = PAGES_DIR / f"{link}.md"
        if not target.exists():
            # 也检查 draft 里有没有
            draft_target = DRAFT_DIR / f"{link}.md"
            if not draft_target.exists():
                result["warnings"].append(f"链接目标不存在: [[{link}]]")

    # 检查文档长度（太短可能是空壳）
    if len(content.strip()) < 100:
        result["errors"].append("文档内容过少（< 100 字符）")
        result["passed"] = False

    # 检查是否有 page_id（从文件名推断）
    page_id = filepath.stem
    if not re.match(r'^[a-z_一-鿿]+$', page_id, re.UNICODE):
        result["warnings"].append(f"文件名建议使用小写+下划线: {page_id}")

    return result


def update_app_map(page_id: str, filepath: Path):
    """将新页面注册到 app_map.json"""
    with open(APP_MAP_PATH, "r", encoding="utf-8") as f:
        app_map = json.load(f)

    if page_id in app_map.get("pages", {}):
        print(f"  [skip] {page_id} 已在 app_map 中")
        return

    # 从文档提取基本信息
    content = filepath.read_text(encoding="utf-8")
    title_match = re.match(r'^# (.+)', content)
    title = title_match.group(1) if title_match else page_id

    # 提取 signature（从关键元素段提取 OCR 文字）
    signature = []
    in_elements = False
    for line in content.split('\n'):
        if '## 关键元素' in line:
            in_elements = True
            continue
        if in_elements and line.startswith('## '):
            break
        if in_elements and '|' in line and 'OCR' in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) > 1:
                signature.append(parts[1])

    app_map["pages"][page_id] = {
        "name": title,
        "type": "page",
        "signature": signature[:5],
        "detail": f"pages/{page_id}.md",
        "promoted_at": datetime.now().isoformat(timespec="minutes"),
    }

    with open(APP_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(app_map, f, ensure_ascii=False, indent=2)

    print(f"  [+] 已注册到 app_map: {page_id}")


def promote_file(filepath: Path, check_only: bool = False) -> bool:
    """验证并转正单个文件"""
    print(f"\n{'='*60}")
    print(f"处理: {filepath.name}")
    print(f"{'='*60}")

    result = validate_draft(filepath)

    # 打印验证结果
    if result["errors"]:
        for e in result["errors"]:
            print(f"  [ERROR] {e}")
    if result["warnings"]:
        for w in result["warnings"]:
            print(f"  [WARN]  {w}")
    if result["links"]:
        print(f"  [LINKS] {', '.join(result['links'])}")

    if not result["passed"]:
        print(f"  [FAIL] 验证未通过，保留在 draft/")
        # 标记为 unverified
        content = filepath.read_text(encoding="utf-8")
        if "<!-- status: unverified -->" not in content:
            content = f"<!-- status: unverified -->\n<!-- validated_at: {datetime.now().isoformat()} -->\n{content}"
            filepath.write_text(content, encoding="utf-8")
        return False

    if check_only:
        print(f"  [OK] 验证通过 (check-only 模式，不转正)")
        return True

    # 转正：移到 pages/
    target = PAGES_DIR / filepath.name
    if target.exists():
        # 如果已存在，备份旧版本
        backup = PAGES_DIR / f"{filepath.stem}.bak.md"
        shutil.copy2(target, backup)
        print(f"  [backup] 已备份旧版本: {backup.name}")

    shutil.move(str(filepath), str(target))
    print(f"  [MOVED] draft/{filepath.name} → pages/{filepath.name}")

    # 更新 app_map
    page_id = filepath.stem
    update_app_map(page_id, target)

    print(f"  [DONE] 转正完成")
    return True


def main():
    parser = argparse.ArgumentParser(description="知识库草稿转正")
    parser.add_argument("--check-only", action="store_true", help="只验证不转正")
    parser.add_argument("--file", type=str, help="指定单个文件")
    args = parser.parse_args()

    if args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            filepath = DRAFT_DIR / args.file
        if not filepath.exists():
            print(f"文件不存在: {args.file}")
            return
        promote_file(filepath, check_only=args.check_only)
    else:
        # 处理 draft/ 下所有 .md 文件
        drafts = list(DRAFT_DIR.glob("*.md"))
        if not drafts:
            print("draft/ 目录为空，没有待转正的文件")
            return

        print(f"发现 {len(drafts)} 个草稿文件")
        passed = 0
        failed = 0
        for f in sorted(drafts):
            if promote_file(f, check_only=args.check_only):
                passed += 1
            else:
                failed += 1

        print(f"\n{'='*60}")
        print(f"总结: {passed} 通过, {failed} 未通过")


if __name__ == "__main__":
    main()
