# -*- coding: utf-8 -*-
"""离线分析源图：用框架同款 PaddleOCR 引擎扫描已保存 PNG，打印全部文字 bbox。
用法：venv/Scripts/python.exe explorer_output/aw_element_tmp/analyze.py <png>...
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from utils.aw.aw_base import AWBase  # noqa: E402

AWBase._get_ocr_engine()


class _Shim:
    _get_ocr_engine = AWBase._get_ocr_engine
    _ocr_use_predict = AWBase._ocr_use_predict


def imread_cn(path: str):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)


def main(argv: list[str]) -> None:
    for path in argv:
        img = imread_cn(path)
        if img is None:
            print(f"[ERR] 无法读取 {path}")
            continue
        h, w = img.shape[:2]
        print(f"=== {os.path.basename(path)} ({w}x{h}) ===")
        items = AWBase._ocr_raw(_Shim(), img)
        for it in sorted(items, key=lambda i: (i["bbox"][1], i["bbox"][0])):
            x1, y1, x2, y2 = it["bbox"]
            print(f"  ({x1:>4},{y1:>4})-({x2:>4},{y2:>4})  {it['text']!r}")


if __name__ == "__main__":
    main(sys.argv[1:])
