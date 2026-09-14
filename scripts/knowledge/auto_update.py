"""
知识库自动更新脚本

在 git commit 后自动执行：
1. 重建 backlinks（如果 pages/*.md 有变更）
2. 增量更新 embedding 索引（如果知识/测试/文档有变更）

用法:
  python scripts/knowledge/auto_update.py                  # 自动检测变更并更新
  python scripts/knowledge/auto_update.py --force          # 强制全量更新
  python scripts/knowledge/auto_update.py --backlinks-only # 只更新 backlinks
  python scripts/knowledge/auto_update.py --embed-only     # 只更新 embedding
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

PROJ_ROOT = Path(__file__).parent.parent.parent
SCRIPTS_DIR = PROJ_ROOT / "scripts" / "knowledge"


def get_changed_files() -> list:
    """获取最近一次 commit 变更的文件(基准可用 KB_DIFF_BASE 覆盖,post-merge 传 ORIG_HEAD)"""
    diff_base = os.environ.get("KB_DIFF_BASE", "HEAD~1")
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", diff_base, "HEAD"],
            capture_output=True, text=True, cwd=str(PROJ_ROOT),
            encoding='utf-8',
        )
        if result.returncode == 0:
            return result.stdout.strip().split('\n')
    except Exception:
        pass
    return []


def needs_backlinks_update(changed_files: list, knowledge_dir: str = "knowledge/web") -> bool:
    """判断是否需要更新 backlinks"""
    prefix = knowledge_dir.replace("\\", "/").rstrip("/") + "/"
    patterns = [f"{prefix}pages/", f"{prefix}digest/"]
    return any(any(p in f for p in patterns) for f in changed_files)


def needs_embedding_update(changed_files: list, knowledge_dir: str = "knowledge/web") -> bool:
    """判断是否需要更新 embedding"""
    patterns = [
        knowledge_dir.replace("\\", "/").rstrip("/") + "/",
        "tests/",
        "docs/",
    ]
    return any(any(p in f for p in patterns) for f in changed_files)


def run_backlinks(knowledge_dir: str = None):
    """运行 backlinks 生成器"""
    print("🔗 更新反向链接...")
    command = [sys.executable, str(SCRIPTS_DIR / "backlinks_generator.py")]
    if knowledge_dir:
        command.extend(["--knowledge-dir", knowledge_dir])
    result = subprocess.run(
        command,
        cwd=str(PROJ_ROOT),
        capture_output=True, text=True, encoding='utf-8',
    )
    if result.returncode == 0:
        print("✅ Backlinks 更新完成")
    else:
        print(f"❌ Backlinks 更新失败: {result.stderr}")
    return result.returncode == 0


def run_embedding(incremental: bool = True, knowledge_dir: str = None, chroma_dir: str = None):
    """运行 embedding pipeline"""
    print("🧠 更新向量索引...")
    args = [sys.executable, str(SCRIPTS_DIR / "embedding_pipeline.py")]
    if incremental:
        args.append("--incremental")
    if knowledge_dir:
        args.extend(["--knowledge-dir", knowledge_dir])
    if chroma_dir:
        args.extend(["--chroma-dir", chroma_dir])

    result = subprocess.run(
        args, cwd=str(PROJ_ROOT),
        capture_output=True, text=True, encoding='utf-8',
    )
    if result.returncode == 0:
        # 输出最后几行（摘要）
        lines = result.stdout.strip().split('\n')
        for line in lines[-6:]:
            print(f"  {line}")
        print("✅ Embedding 更新完成")
    else:
        print(f"❌ Embedding 更新失败: {result.stderr[-200:]}")
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="知识库自动更新")
    parser.add_argument("--force", action="store_true", help="强制全量更新")
    parser.add_argument("--backlinks-only", action="store_true", help="只更新 backlinks")
    parser.add_argument("--embed-only", action="store_true", help="只更新 embedding")
    parser.add_argument("--knowledge-dir", type=str, help="知识库目录（默认 Web 知识库）")
    parser.add_argument("--chroma-dir", type=str, help="向量数据库目录（默认 .chroma_db）")
    args = parser.parse_args()

    print("=" * 60)
    print("📚 知识库自动更新")
    print("=" * 60)

    if args.force:
        print("模式: 强制全量更新")
        run_backlinks(args.knowledge_dir)
        run_embedding(incremental=False, knowledge_dir=args.knowledge_dir, chroma_dir=args.chroma_dir)
        return

    if args.backlinks_only:
        run_backlinks(args.knowledge_dir)
        return

    if args.embed_only:
        run_embedding(incremental=True, knowledge_dir=args.knowledge_dir, chroma_dir=args.chroma_dir)
        return

    # 自动检测变更
    changed_files = get_changed_files()
    if not changed_files or changed_files == ['']:
        print("未检测到变更文件，跳过更新")
        return

    print(f"检测到 {len(changed_files)} 个变更文件")

    knowledge_dir = args.knowledge_dir or "knowledge/web"
    if needs_backlinks_update(changed_files, knowledge_dir):
        run_backlinks(args.knowledge_dir)
    else:
        print("⏭️  知识库页面无变更，跳过 backlinks")

    if needs_embedding_update(changed_files, knowledge_dir):
        run_embedding(incremental=True, knowledge_dir=args.knowledge_dir, chroma_dir=args.chroma_dir)
    else:
        print("⏭️  相关文件无变更，跳过 embedding")

    print("\n✅ 自动更新完成")


if __name__ == "__main__":
    main()
