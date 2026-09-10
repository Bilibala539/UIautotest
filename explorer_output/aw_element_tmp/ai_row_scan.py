# -*- coding: utf-8 -*-
"""AI Tab 入口行精细分析：行剖面 + 小连通域。"""
import os
import sys

sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from probe import imread_cn  # noqa: E402

img = imread_cn(r"E:\UIAutotest\explorer_output\aw_element_tmp\src_home_ai.png")

# 行剖面：y=737 与 y=700 / 770（按钮上下缘附近）
for y in (700, 716, 737, 760, 776):
    row = img[y, 150:720]
    segs = []
    start = 0
    for i in range(1, len(row)):
        if any(abs(int(a) - int(b)) > 5 for a, b in zip(row[start], row[i])):
            segs.append((start + 150, i - 1 + 150, tuple(int(v) for v in row[start])))
            start = i
    segs.append((start + 150, 719, tuple(int(v) for v in row[start])))
    print(f"y={y}:", [s for s in segs if s[1] - s[0] >= 3])

# 列剖面 x=300（添加角色 pill 中间）与 x=570（图标列）
for x in (300, 570, 640):
    col = img[660:830, x]
    segs = []
    start = 0
    for i in range(1, len(col)):
        if any(abs(int(a) - int(b)) > 5 for a, b in zip(col[start], col[i])):
            segs.append((start + 660, i - 1 + 660, tuple(int(v) for v in col[start])))
            start = i
    segs.append((start + 660, 829, tuple(int(v) for v in col[start])))
    print(f"x={x}:", [s for s in segs if s[1] - s[0] >= 3])

# 小字检测：区域 (519,696)-(617,778) 内 tol=4 的连通域
roi = img[690:790, 500:720]
quant = (roi // 4 * 4).reshape(-1, 3)
from collections import Counter  # noqa: E402
bg = Counter(map(tuple, quant)).most_common(1)[0][0]
dist = np.abs(roi.astype(int) - np.array(bg, dtype=int)).sum(axis=2)
for tol in (4, 10, 16):
    mask = (dist > tol * 3).astype(np.uint8)
    mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)))
    n, _, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    comps = [(sx + 500, sy + 690, sx + w + 500, sy + h + 690, a)
             for i in range(1, n) for sx, sy, w, h, a in [stats[i]] if a >= 20]
    print(f"tol={tol} bg={bg}:", sorted(comps, key=lambda c: c[0]))
