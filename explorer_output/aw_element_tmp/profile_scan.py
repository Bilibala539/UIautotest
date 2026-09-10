# -*- coding: utf-8 -*-
"""搜索条 pill 边界探测：行/列颜色分段。"""
import os
import sys

sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")

from probe import imread_cn  # noqa: E402

OUT = r"E:\UIAutotest\explorer_output\aw_element_tmp"


def segments(vals, lo, hi, tol=8, min_len=4):
    segs = []
    start = 0
    for i in range(1, len(vals)):
        a, b = vals[start], vals[i]
        if any(abs(int(x) - int(y)) > tol for x, y in zip(a, b)):
            segs.append((start + lo, i - 1 + lo, tuple(int(v) for v in a)))
            start = i
    segs.append((start + lo, hi, tuple(int(v) for v in vals[start])))
    return [s for s in segs if s[1] - s[0] >= min_len]


for name, ymid in [("src_home_music.png", 245), ("src_home_radio.png", 240)]:
    img = imread_cn(os.path.join(OUT, name))
    row = img[ymid]
    print(name, "row y=%d" % ymid, segments(list(row), 0, 719))
    col = img[:, 360]
    print(name, "col x=360", segments(list(col[150:400]), 150, 399))
