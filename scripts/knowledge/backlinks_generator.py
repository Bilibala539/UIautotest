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
from pathlib import Path
from datetime import datetime

KNOWLEDGE_DIR = Path("explorer_output/knowledge")
PAGES_DIR = KNOWLEDGE_DIR / "pages"
DIGEST_DIR = KNOWLEDGE_DIR / "digest"
BACKLINKS_PATH = KNOWLEDGE_DIR / "backlinks.json"

LINK_PATTERN = re.compile(r'\[\[([^\]]+)\]\]')
BACKLINKS_SECTION = "## 反向引用"
BACKLINKS_MARKER_START = "<!-- backlinks:start -->"
BACKLINKS_MARKER_END = "<!-- backlinks:end -->"


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
                rel_path = str(md_file.relative_to(KNOWLEDGE_DIR))
                forward_index[rel_path] = list(set(links))

    return forward_index


def build_backlinks_index(forward_index: dict) -> dict:
    """从正向索引构建反向索引"""
    backlinks = {}  # {target_id: [{source, context}]}

    for source_file, targets in forward_index.items():
        source_id = Path(source_file).stem
        for target in targets:
            if target not in backlinks:
                backlinks[target] = []
            backlinks[target].append({
                "source": source_file,
                "source_id": source_id,
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
    args = parser.parse_args()

    print("扫描知识库中的 [[链接]]...")
    forward_index = scan_all_links()

    total_links = sum(len(v) for v in forward_index.values())
    print(f"发现 {len(forward_index)} 个文件包含 {total_links} 条链接")

    print("\n构建反向索引...")
    backlinks_index = build_backlinks_index(forward_index)
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

    # 注入到对应文件
    print("\n注入反向引用段到文件...")
    injected = 0
    for target_id, sources in backlinks_index.items():
        # 查找对应文件
        target_file = PAGES_DIR / f"{target_id}.md"
        if not target_file.exists():
            # 尝试中文文件名
            for md in PAGES_DIR.glob("*.md"):
                if md.stem == target_id:
                    target_file = md
                    break
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
