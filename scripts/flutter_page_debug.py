"""Flutter 页面一键调试：截图 + 语义树 dump + OCR 一次完成。

explorer 探索、key 校验、verify 诊断的入口工具：

    python scripts/flutter_page_debug.py                     # 默认设备
    python scripts/flutter_page_debug.py --serial <serial>   # 指定设备
    python scripts/flutter_page_debug.py --clickable         # 语义树只保留可点击节点

输出目录：explorer_output/flutter_debug/<时间戳>/
    screenshot.png   当前页面截图
    semantics.txt    语义树可读表格（clickable / resource_id / text / bounds）
    semantics.json   语义树原始数据
    ocr.txt          OCR 识别到的全部文本
"""
from __future__ import annotations

import argparse
import io
import json
import logging
import sys
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.aw.base.flutter_base import FlutterBaseAW
from utils.aw.driver.android_driver import AndroidAdbDriver


def main() -> int:
    parser = argparse.ArgumentParser(description="Flutter 页面一键调试（截图+dump+OCR）")
    parser.add_argument("--serial", default=None, help="adb 设备 serial（默认 ANDROID_DEVICE_SERIAL 或唯一设备）")
    parser.add_argument("--out", default=None, help="输出目录（默认 explorer_output/flutter_debug/<时间戳>）")
    parser.add_argument("--clickable", action="store_true", help="语义树只打印可点击节点")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    driver = AndroidAdbDriver(serial=args.serial)
    aw = FlutterBaseAW(driver)

    out_dir = Path(args.out) if args.out else (
        PROJECT_ROOT / "explorer_output" / "flutter_debug" / datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. 截图
    screenshot_path = out_dir / "screenshot.png"
    aw.take_screenshot(save_path=str(screenshot_path))

    # 2. 语义树 dump
    nodes = aw.dump_semantics()
    (out_dir / "semantics.json").write_text(
        json.dumps(nodes, ensure_ascii=False, indent=2), encoding="utf-8")
    buf = io.StringIO()
    with redirect_stdout(buf):
        aw.print_semantics(clickable_only=args.clickable)
    (out_dir / "semantics.txt").write_text(buf.getvalue(), encoding="utf-8")

    # 3. OCR
    ocr_items = aw.ocr_scan_page()
    ocr_lines = []
    for item in ocr_items:
        text = item.get("text", "") if isinstance(item, dict) else str(item)
        ocr_lines.append(text)
    (out_dir / "ocr.txt").write_text("\n".join(ocr_lines), encoding="utf-8")

    print(f"\n输出目录: {out_dir}")
    print(f"语义节点: {len(nodes)} 个（semantics.txt / semantics.json）")
    print(f"OCR 文本: {len(ocr_lines)} 条（ocr.txt）")
    print(f"截图: {screenshot_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
