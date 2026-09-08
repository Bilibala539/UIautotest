"""
反向链接生成器

扫描 pages/*.md 中所有 [[link]] 标记，构建反向索引，
并将 ## 反向引用 段写入每个被引用的文件。

产出:
  1. backlinks.json — 完整反向索引（供 MCP Server 查询）
  2. 每个 .md 文件底部的 ## 反向引用 段（供 agent 直接阅读）

用法:
  python scripts/knowledge/backlinks_generator.py              # 全量重建
  python scripts/knowledge/backlinks_generator.py --dry-run    # 只输出不写入
"""

import re
import json
import argparse
import os
from pathlib import Path
from datetime import datetime

PROJ_ROOT = Path(__file__).parent.parent.parent
KNOWLEDGE_DIR = Path(os.environ.get("UIAUTOTEST_KNOWLEDGE_DIR", PROJ_ROOT / "knowledge/web"))
if not KNOWLEDGE_DIR.is_absolute():
    KNOWLEDGE_DIR = PROJ_ROOT / KNOWLEDGE_DIR
PAGES_DIR = KNOWLEDGE_DIR / "pages"
DIGEST_DIR = KNOWLEDGE_DIR / "digest"
BACKLINKS_PATH = KNOWLEDGE_DIR / "backlinks.json"

LINK_PATTERN = re.compile(r'\[\[([^\]]+)\]\]')
BACKLINKS_SECTION = "## 反向引用"
BACKLINKS_MARKER_START = "<!-- backlinks:start -->"
BACKLINKS_MARKER_END = "<!-- backlinks:end -->"
FRONTMATTER_PATTERN = re.compile(r'^---\n(.*?)\n---\n', re.DOTALL)


def parse_frontmatter_aliases(content: str) -> tuple:
    """从 YAML frontmatter 提取 (page_id, [aliases])。
    最小手解析，不引入 yaml 依赖。
    """
    m = FRONTMATTER_PATTERN.match(content)
    if not m:
        return None, []
    body = m.group(1)
    page_id = None
    aliases = []
    cur_key = None
    in_aliases_block = False
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


def build_alias_map(scan_dirs) -> dict:
    """扫 pages/ 与 digest/，建立 alias/page_id → 主 stem 的映射。
    返回: {alias_or_pageid_or_stem: real_stem}
    """
    amap = {}
    for d in scan_dirs:
        if not d.exists():
            continue
        for f in d.rglob("*.md"):
            stem = f.stem
            amap.setdefault(stem, stem)  # stem 自己
            try:
                content = f.read_text(encoding="utf-8")
            except Exception:
                continue
            pid, aliases = parse_frontmatter_aliases(content)
            if pid:
                amap.setdefault(pid, stem)
            for a in aliases:
                amap.setdefault(a, stem)
    return amap


def scan_all_links() -> dict:
    """扫描所有 md 文件，提取 [[link]] 构建正向索引"""
    forward_index = {}  # {source_file: [target_ids]}

    # 扫描 pages/ 和 digest/
    scan_dirs = [PAGES_DIR, DIGEST_DIR]
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for md_file in scan_dir.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            # 排除 backlinks 段内的链接（避免循环）
            content_clean = re.sub(
                f'{BACKLINKS_MARKER_START}.*?{BACKLINKS_MARKER_END}',
                '', content, flags=re.DOTALL
            )
            links = LINK_PATTERN.findall(content_clean)
            if links:
                rel_path = md_file.relative_to(KNOWLEDGE_DIR).as_posix()
                forward_index[rel_path] = list(set(links))

    return forward_index


def build_backlinks_index(forward_index: dict, alias_map: dict = None) -> dict:
    """从正向索引构建反向索引。
    若提供 alias_map，会把每个 link 解析到真正的 stem，再做反向归并；
    否则保留原 link 文本。
    """
    backlinks = {}  # {target_stem: [{source, source_id}]}

    for source_file, targets in forward_index.items():
        source_id = Path(source_file).stem
        for target in targets:
            real = (alias_map or {}).get(target, target)
            if real not in backlinks:
                backlinks[real] = []
            # 去重：同一来源不重复
            if not any(b["source"] == source_file for b in backlinks[real]):
                backlinks[real].append({
                    "source": source_file,
                    "source_id": source_id,
                    "raw_link": target,
                })

    return backlinks


def inject_backlinks_section(filepath: Path, backlinks: list, dry_run: bool = False) -> bool:
    """在文件末尾注入或更新反向引用段"""
    content = filepath.read_text(encoding="utf-8")

    # 构建 backlinks 段内容
    lines = [
        "",
        BACKLINKS_SECTION,
        BACKLINKS_MARKER_START,
        "",
        "| 引用来源 | 页面ID |",
        "|---------|--------|",
    ]
    for bl in sorted(backlinks, key=lambda x: x["source_id"]):
        lines.append(f"| {bl['source']} | [[{bl['source_id']}]] |")
    lines.append("")
    lines.append(f"_自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}_")
    lines.append(BACKLINKS_MARKER_END)

    new_section = "\n".join(lines)

    # 替换已有的 backlinks 段，或追加到末尾
    if BACKLINKS_MARKER_START in content:
        content = re.sub(
            f'{BACKLINKS_SECTION}\n{BACKLINKS_MARKER_START}.*?{BACKLINKS_MARKER_END}',
            new_section.lstrip('\n'),
            content,
            flags=re.DOTALL
        )
    else:
        content = content.rstrip('\n') + "\n" + new_section

    if dry_run:
        print(f"  [dry-run] 将写入 {filepath.name}: {len(backlinks)} 条反向引用")
        return True

    filepath.write_text(content, encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description="知识库反向链接生成器")
    parser.add_argument("--dry-run", action="store_true", help="只输出不写入")
    parser.add_argument("--knowledge-dir", type=str, help="知识库目录（默认 Web 知识库）")
    args = parser.parse_args()

    global KNOWLEDGE_DIR, PAGES_DIR, DIGEST_DIR, BACKLINKS_PATH
    if args.knowledge_dir:
        KNOWLEDGE_DIR = Path(args.knowledge_dir)
        if not KNOWLEDGE_DIR.is_absolute():
            KNOWLEDGE_DIR = PROJ_ROOT / KNOWLEDGE_DIR
        PAGES_DIR = KNOWLEDGE_DIR / "pages"
        DIGEST_DIR = KNOWLEDGE_DIR / "digest"
        BACKLINKS_PATH = KNOWLEDGE_DIR / "backlinks.json"

    print("扫描知识库中的 [[链接]]...")
    forward_index = scan_all_links()

    total_links = sum(len(v) for v in forward_index.values())
    print(f"发现 {len(forward_index)} 个文件包含 {total_links} 条链接")

    print("\n构建 alias 映射...")
    # alias 映射也扫 draft/，避免 pages 中链接指向 draft 占位时被判 broken
    alias_map = build_alias_map([PAGES_DIR, DIGEST_DIR, KNOWLEDGE_DIR / "draft"])
    print(f"alias 映射条目数: {len(alias_map)}")

    print("\n构建反向索引...")
    backlinks_index = build_backlinks_index(forward_index, alias_map)
    print(f"生成 {len(backlinks_index)} 个目标的反向引用")

    # 保存 backlinks.json
    if not args.dry_run:
        output = {
            "generated_at": datetime.now().isoformat(),
            "stats": {
                "source_files": len(forward_index),
                "total_links": total_links,
                "target_pages": len(backlinks_index),
            },
            "forward_index": forward_index,
            "backlinks": backlinks_index,
        }
        with open(BACKLINKS_PATH, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\n已保存: {BACKLINKS_PATH}")

    # 注入到对应文件（按 alias_map 已解析后的真 stem 查找；同时考虑 draft/）
    print("\n注入反向引用段到文件...")
    injected = 0
    DRAFT = KNOWLEDGE_DIR / "draft"
    for target_id, sources in backlinks_index.items():
        target_file = PAGES_DIR / f"{target_id}.md"
        if not target_file.exists():
            target_file = DRAFT / f"{target_id}.md"
        if not target_file.exists():
            # 兜底：遍历 pages 和 draft 比较 stem
            cand = None
            for d in (PAGES_DIR, DRAFT):
                for md in d.glob("*.md"):
                    if md.stem == target_id:
                        cand = md
                        break
                if cand:
                    break
            if cand:
                target_file = cand
            else:
                print(f"  [skip] 目标文件不存在: {target_id}.md")
                continue

        inject_backlinks_section(target_file, sources, dry_run=args.dry_run)
        injected += 1

    print(f"\n完成: 注入了 {injected} 个文件的反向引用")
    if args.dry_run:
        print("(dry-run 模式，未实际写入)")


if __name__ == "__main__":
    main()
