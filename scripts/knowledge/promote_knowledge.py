"""
知识库草稿转正脚本

流程:
  1. explorer 写新发现到 draft/ 目录
  2. 本脚本验证草稿质量（结构完整性 + 链接有效性）
  3. 交叉引用发现：搜索已有 pages 中提到新页面关键词的文档，自动补充双向链接
  4. 验证通过 → 移入 pages/ + 更新 app_map.json + 触发 re-embed
  5. 验证失败 → 保留在 draft/ 标记 unverified

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

PROJ_ROOT = Path(__file__).parent.parent.parent
KNOWLEDGE_DIR = Path(os.environ.get("UIAUTOTEST_KNOWLEDGE_DIR", PROJ_ROOT / "knowledge/web"))
if not KNOWLEDGE_DIR.is_absolute():
    KNOWLEDGE_DIR = PROJ_ROOT / KNOWLEDGE_DIR
DRAFT_DIR = KNOWLEDGE_DIR / "draft"
PAGES_DIR = KNOWLEDGE_DIR / "pages"
APP_MAP_PATH = KNOWLEDGE_DIR / "app_map.json"

REQUIRED_SECTIONS = ["## 页面概述", "## 进入方式", "## 关键元素"]
LINK_PATTERN = re.compile(r'\[\[([^\]]+)\]\]')
FRONTMATTER_PATTERN = re.compile(r'^---\n.*?\n---\n', re.DOTALL)


def strip_frontmatter(content: str) -> str:
    """剥掉 YAML frontmatter，返回正文。无 frontmatter 时原样返回。"""
    return FRONTMATTER_PATTERN.sub('', content, count=1)


def find_first_heading(body: str) -> str:
    """跳过空行和 HTML 注释，返回首个真实段落。供 startswith # 检查使用。"""
    for line in body.split('\n'):
        s = line.strip()
        if not s:
            continue
        if s.startswith('<!--') and s.endswith('-->'):
            continue
        return line
    return ""


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
    body = strip_frontmatter(content)

    # 检查标题（跳过空行和 HTML 注释定位首个段落）
    first = find_first_heading(body)
    if not first.lstrip().startswith("# "):
        result["errors"].append("缺少一级标题")
        result["passed"] = False

    # 检查必要章节
    for section in REQUIRED_SECTIONS:
        if section not in body:
            result["warnings"].append(f"缺少章节: {section}")

    # 检查链接有效性
    links = LINK_PATTERN.findall(body)
    result["links"] = links
    for link in links:
        target = PAGES_DIR / f"{link}.md"
        if not target.exists():
            # 也检查 draft 里有没有
            draft_target = DRAFT_DIR / f"{link}.md"
            # feature_/flow_ 前缀的链接指向 digest/features|flows/（见 templates/page.md 功能关联）
            digest_target = None
            if link.startswith("feature_"):
                digest_target = KNOWLEDGE_DIR / "digest" / "features" / f"{link}.md"
            elif link.startswith("flow_"):
                digest_target = KNOWLEDGE_DIR / "digest" / "flows" / f"{link}.md"
            if not (draft_target.exists()
                    or (digest_target is not None and digest_target.exists())):
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
    body = strip_frontmatter(content)
    title_match = re.match(r'^# (.+)', body.lstrip())
    title = title_match.group(1) if title_match else page_id

    # 提取 signature（从关键元素段提取 OCR 文字）
    signature = []
    in_elements = False
    for line in body.split('\n'):
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


def discover_cross_references(filepath: Path) -> list:
    """
    通过核心关键词全文搜索，发现已有 pages 中与新页面相关但未建立链接的文档。

    策略：
    1. 从新页面标题提取核心功能词（去掉通用后缀如"操作/管理/设置/页面"）
    2. 在所有已有 pages 中 grep 该核心词
    3. 命中但未建立 [[link]] 的 = 缺失的交叉引用

    Returns:
        list of dict: [{page_file, page_id, keyword, suggestion}]
    """
    content = filepath.read_text(encoding="utf-8")
    body = strip_frontmatter(content)
    new_page_id = filepath.stem

    # 从一级标题提取核心功能词
    title_match = re.match(r'^# (.+)', body.lstrip())
    if not title_match:
        return []
    title = title_match.group(1).strip()

    # 生成搜索词：完整标题 + 去后缀版本
    search_terms = set()
    search_terms.add(title)
    suffixes = ['操作', '管理', '设置', '页面', '功能', '列表', '详情', '相关', '流程']
    for suffix in suffixes:
        if title.endswith(suffix) and len(title) > len(suffix) + 1:
            search_terms.add(title[:-len(suffix)])
    # 按分隔符拆分（处理"P2P设置页面"这类）
    for word in re.split(r'[（）()、/\s\-_]+', title):
        if len(word) >= 3:
            search_terms.add(word)
            for suffix in suffixes:
                if word.endswith(suffix) and len(word) > len(suffix) + 1:
                    search_terms.add(word[:-len(suffix)])

    # 过滤通用词（含项目前缀与泛用 ASCII 词——"swan" 会命中知识库所有页面，产生大量假阳性）
    stopwords = {'页面', '设置', '管理', '操作', '功能', '列表', '消息', '详情',
                 'swan', 'web', 'android', 'app', 'tab', 'Tab'}
    search_terms -= stopwords

    if not search_terms:
        return []

    # 在已有 pages 中全文搜索
    missing_refs = []
    for page_file in PAGES_DIR.glob("*.md"):
        if page_file.stem == new_page_id:
            continue
        page_content = page_file.read_text(encoding="utf-8")

        # 检查对方是否已链接到新页面
        existing_links = set(LINK_PATTERN.findall(page_content))
        if new_page_id in existing_links:
            continue

        # 按词长倒序匹配（优先长词，更精确）
        matched_term = None
        for term in sorted(search_terms, key=len, reverse=True):
            if term in page_content:
                matched_term = term
                break

        if matched_term:
            missing_refs.append({
                "page_file": page_file.name,
                "page_id": page_file.stem,
                "keyword": matched_term,
                "suggestion": f"[[{new_page_id}]]",
            })

    return missing_refs


def inject_cross_references(new_page: Path, missing_refs: list):
    """
    在新页面的关联表格中补充对已有页面的引用。
    同时在已有页面的关联表格中添加回链。
    格式统一为: | [[page_id]] | 关系类型 | 说明 |
    """
    if not missing_refs:
        return

    new_page_id = new_page.stem
    content = new_page.read_text(encoding="utf-8")

    # 在新页面的关联表格末尾追加行
    additions = []
    for ref in missing_refs:
        link = f"[[{ref['page_id']}]]"
        if link not in content:
            additions.append(f"| {link} | feature | {ref['keyword']} |")

    if additions:
        # 找关联表格的最后一行 (| [[xxx]] | ... | 格式)
        table_pattern = re.compile(r'(\| \[\[.+?\]\].+\|.+\|)\n')
        matches = list(table_pattern.finditer(content))
        if matches:
            last_row = matches[-1]
            new_rows = '\n'.join(additions) + '\n'
            content = content[:last_row.end()] + new_rows + content[last_row.end():]
            new_page.write_text(content, encoding="utf-8")
            print(f"  [XREF+] 新页面补充了 {len(additions)} 个交叉引用")

    # 在已有页面的关联表格中添加回链
    for ref in missing_refs:
        page_path = PAGES_DIR / ref["page_file"]
        page_content = page_path.read_text(encoding="utf-8")
        back_link = f"[[{new_page_id}]]"
        if back_link in page_content:
            continue

        # 找关联表格的最后一行
        table_pattern = re.compile(r'(\| \[\[.+?\]\].+\|.+\|)\n')
        matches = list(table_pattern.finditer(page_content))
        if matches:
            last_row = matches[-1]
            new_row = f"| {back_link} | feature | {ref['keyword']} |\n"
            page_content = page_content[:last_row.end()] + new_row + page_content[last_row.end():]
            page_path.write_text(page_content, encoding="utf-8")
            print(f"  [XREF←] {ref['page_file']} 已添加回链 {back_link}")


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

    # 交叉引用发现：搜索已有页面中提到新页面关键词的文档
    missing_refs = discover_cross_references(target)
    if missing_refs:
        print(f"  [XREF] 发现 {len(missing_refs)} 个缺失的交叉引用:")
        for ref in missing_refs:
            print(f"         {ref['page_file']} (关键词: {ref['keyword']})")
        inject_cross_references(target, missing_refs)
    else:
        print(f"  [XREF] 无缺失交叉引用")

    # 更新 app_map
    page_id = filepath.stem
    update_app_map(page_id, target)

    print(f"  [DONE] 转正完成")
    return True


def run_post_promote():
    """转正后自动重建 backlinks + 增量更新向量索引（作用于当前 --knowledge-dir 指定的知识库）"""
    import subprocess
    import sys

    scripts_dir = Path("scripts/knowledge")

    print(f"\n{'='*60}")
    print(f"  转正后自动更新索引（知识库: {KNOWLEDGE_DIR}）...")
    print(f"{'='*60}")

    # 重建反向链接
    print("  [1/2] 重建反向链接...")
    result = subprocess.run(
        [sys.executable, str(scripts_dir / "backlinks_generator.py"),
         "--knowledge-dir", str(KNOWLEDGE_DIR)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if result.returncode == 0:
        print("  [OK] 反向链接重建完成")
    else:
        print(f"  [WARN] 反向链接重建异常: {result.stderr[-200:]}")

    # 增量更新向量索引
    print("  [2/2] 增量更新向量索引...")
    env = os.environ.copy()
    env.setdefault("UIAUTOTEST_EMBEDDING_MODEL",
                   str(PROJ_ROOT / "models" / "paraphrase-multilingual-MiniLM-L12-v2"))
    result = subprocess.run(
        [sys.executable, str(scripts_dir / "embedding_pipeline.py"),
         "--knowledge-dir", str(KNOWLEDGE_DIR),
         "--chroma-dir", str(KNOWLEDGE_DIR / ".chroma_db"),
         "--incremental"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env
    )
    if result.returncode == 0:
        # 提取最后几行输出
        lines = result.stdout.strip().split('\n')
        for line in lines[-4:]:
            if line.strip():
                print(f"        {line.strip()}")
        print("  [OK] 向量索引更新完成")
    else:
        print(f"  [WARN] 向量索引更新异常: {result.stderr[-200:]}")


def main():
    parser = argparse.ArgumentParser(description="知识库草稿转正")
    parser.add_argument("--check-only", action="store_true", help="只验证不转正")
    parser.add_argument("--file", type=str, help="指定单个文件")
    parser.add_argument("--knowledge-dir", type=str, help="知识库目录（默认 Web 知识库）")
    args = parser.parse_args()

    global KNOWLEDGE_DIR, DRAFT_DIR, PAGES_DIR, APP_MAP_PATH
    if args.knowledge_dir:
        KNOWLEDGE_DIR = Path(args.knowledge_dir)
        if not KNOWLEDGE_DIR.is_absolute():
            KNOWLEDGE_DIR = PROJ_ROOT / KNOWLEDGE_DIR
        DRAFT_DIR = KNOWLEDGE_DIR / "draft"
        PAGES_DIR = KNOWLEDGE_DIR / "pages"
        APP_MAP_PATH = KNOWLEDGE_DIR / "app_map.json"

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

    # 有文件转正成功时，自动更新索引
    if not args.check_only:
        run_post_promote()


if __name__ == "__main__":
    main()
