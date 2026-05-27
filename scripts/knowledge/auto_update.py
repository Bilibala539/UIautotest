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
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

PROJ_ROOT = Path(__file__).parent.parent.parent
SCRIPTS_DIR = PROJ_ROOT / "scripts" / "knowledge"


def get_changed_files() -> list:
    """获取最近一次 commit 变更的文件"""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True, text=True, cwd=str(PROJ_ROOT),
            encoding='utf-8',
        )
        if result.returncode == 0:
            return result.stdout.strip().split('\n')
    except Exception:
        pass
    return []


def needs_backlinks_update(changed_files: list) -> bool:
    """判断是否需要更新 backlinks"""
    patterns = ["explorer_output/knowledge/pages/", "explorer_output/knowledge/digest/"]
    return any(any(p in f for p in patterns) for f in changed_files)


def needs_embedding_update(changed_files: list) -> bool:
    """判断是否需要更新 embedding"""
    patterns = [
        "explorer_output/knowledge/",
        "tests/",
        "docs/",
    ]
    return any(any(p in f for p in patterns) for f in changed_files)


def run_backlinks():
    """运行 backlinks 生成器"""
    print("🔗 更新反向链接...")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "backlinks_generator.py")],
        cwd=str(PROJ_ROOT),
        capture_output=True, text=True, encoding='utf-8',
    )
    if result.returncode == 0:
        print("✅ Backlinks 更新完成")
    else:
        print(f"❌ Backlinks 更新失败: {result.stderr}")
    return result.returncode == 0


def run_embedding(incremental: bool = True):
    """运行 embedding pipeline"""
    print("🧠 更新向量索引...")
    args = [sys.executable, str(SCRIPTS_DIR / "embedding_pipeline.py")]
    if incremental:
        args.append("--incremental")

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
    import argparse
    parser = argparse.ArgumentParser(description="知识库自动更新")
    parser.add_argument("--force", action="store_true", help="强制全量更新")
    parser.add_argument("--backlinks-only", action="store_true", help="只更新 backlinks")
    parser.add_argument("--embed-only", action="store_true", help="只更新 embedding")
    args = parser.parse_args()

    print("=" * 60)
    print("📚 知识库自动更新")
    print("=" * 60)

    if args.force:
        print("模式: 强制全量更新")
        run_backlinks()
        run_embedding(incremental=False)
        return

    if args.backlinks_only:
        run_backlinks()
        return

    if args.embed_only:
        run_embedding(incremental=True)
        return

    # 自动检测变更
    changed_files = get_changed_files()
    if not changed_files or changed_files == ['']:
        print("未检测到变更文件，跳过更新")
        return

    print(f"检测到 {len(changed_files)} 个变更文件")

    if needs_backlinks_update(changed_files):
        run_backlinks()
    else:
        print("⏭️  知识库页面无变更，跳过 backlinks")

    if needs_embedding_update(changed_files):
        run_embedding(incremental=True)
    else:
        print("⏭️  相关文件无变更，跳过 embedding")

    print("\n✅ 自动更新完成")


if __name__ == "__main__":
    main()
