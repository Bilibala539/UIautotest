"""使用 pytest-xdist 并行执行 Web 测试。"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="并行执行 TidiTree Web 测试")
    parser.add_argument("-n", "--workers", default="auto", help="worker 数量，默认 auto")
    parser.add_argument("-t", "--limit", type=int, default=None, help="仅执行前 N 个测试文件")
    parser.add_argument("--test-dir", default="tests", help="测试目录")
    parser.add_argument("pytest_args", nargs=argparse.REMAINDER, help="传给 pytest 的其他参数")
    args = parser.parse_args()

    test_dir = Path(args.test_dir)
    if not test_dir.exists():
        parser.error(f"测试目录不存在: {test_dir}")

    targets = sorted(test_dir.rglob("test_*.py"))
    if args.limit is not None:
        targets = targets[:args.limit]
    if not targets:
        print(f"未找到测试文件: {test_dir}/**/test_*.py")
        return 0

    command = [sys.executable, "-m", "pytest", "-n", str(args.workers), *map(str, targets), *args.pytest_args]
    environment = os.environ.copy()
    environment.setdefault("PLATFORM", "web")
    return subprocess.run(command, cwd=Path(__file__).parent, env=environment).returncode


if __name__ == "__main__":
    raise SystemExit(main())
