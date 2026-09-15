"""APK 注册脚本(步骤 10 构建产物入口)。

把一个 APK 文件注册进平台包管理,返回 apk_id(供执行会话/流水线任务关联)。
用法:
  python scripts/register_apk.py E:\\swan\\swan-audio-1.2.3.apk \
      --version 1.2.3 --branch main --flavor prod --source dev
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

PLATFORM_URL = os.environ.get("DASHBOARD_URL", "http://192.168.12.166:8080").rstrip("/")


def main() -> int:
    parser = argparse.ArgumentParser(description="注册 APK 进平台包管理")
    parser.add_argument("apk_path", help="APK 文件路径")
    parser.add_argument("--version", default="", help="应用版本号")
    parser.add_argument("--branch", default="", help="来源分支")
    parser.add_argument("--flavor", default="", help="渠道/flavor(如 prod)")
    parser.add_argument("--source", default="manual", help="来源(manual/pipeline/dev)")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    apk = Path(args.apk_path)
    if not apk.is_file():
        print(f"文件不存在: {apk}")
        return 1
    file_hash = hashlib.sha256(apk.read_bytes()).hexdigest()

    payload = {
        "app_version": args.version,
        "branch": args.branch,
        "flavor": args.flavor,
        "source": args.source,
        "file_path": str(apk),
        "file_hash": file_hash,
        "notes": f"size={apk.stat().st_size}",
    }
    request = urllib.request.Request(
        f"{PLATFORM_URL}/api/apks",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        result = json.loads(response.read().decode("utf-8"))
    print(f"已注册 apk_id={result.get('apk_id')} hash={file_hash[:12]}…")
    return 0


if __name__ == "__main__":
    sys.exit(main())
