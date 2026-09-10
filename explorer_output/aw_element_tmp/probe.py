# -*- coding: utf-8 -*-
"""像素连通域探测：在指定区域内找与背景色差异显著的连通内容块，输出 bbox。

用法：venv/Scripts/python.exe explorer_output/aw_element_tmp/probe.py <png> x1 y1 x2 y2 [tol] [min_area]
"""
from __future__ import annotations

import os
import sys
from collections import Counter

sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")

import cv2  # noqa: E402
import numpy as np  # noqa: E402


def imread_cn(path: str):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)


def probe(path: str, x1: int, y1: int, x2: int, y2: int, tol: int = 12,
          min_area: int = 40) -> None:
    img = imread_cn(path)
    if img is None:
        print(f"[ERR] 无法读取 {path}")
        return
    roi = img[y1:y2, x1:x2]
    # 背景色 = 区域内最常见颜色（量化到 8 级减少噪声）
    quant = (roi // 8 * 8).reshape(-1, 3)
    bg = Counter(map(tuple, quant)).most_common(1)[0][0]
    dist = np.abs(roi.astype(int) - np.array(bg, dtype=int)).sum(axis=2)
    mask = (dist > tol * 3).astype(np.uint8)
    # 轻度膨胀合并相邻笔画
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    mask = cv2.dilate(mask, kernel)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    print(f"=== {os.path.basename(path)} roi=({x1},{y1})-({x2},{y2}) bg={bg} tol={tol} ===")
    comps = []
    for i in range(1, n):
        cx, cy, cw, ch, area = stats[i]
        if area < min_area:
            continue
        comps.append((cy + y1, cx + x1, cx + cw + x1, cy + ch + y1, area))
    for gy, gx1, gx2, gyy, area in sorted(comps):
        print(f"  bbox=({gx1},{gy})-({gx2},{gyy})  size={gx2-gx1}x{gyy-gy}  area={area}")


if __name__ == "__main__":
    a = sys.argv
    probe(a[1], int(a[2]), int(a[3]), int(a[4]), int(a[5]),
          int(a[6]) if len(a) > 6 else 12,
          int(a[7]) if len(a) > 7 else 40)
