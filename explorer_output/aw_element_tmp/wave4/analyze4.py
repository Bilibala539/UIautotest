# -*- coding: utf-8 -*-
"""Wave4 裁剪框像素分析：从源图区域中找内容紧贴 bbox（背景色差阈值法）。"""
from __future__ import annotations

import os
import sys

import cv2
import numpy as np

OUT = r"E:\UIAutotest\explorer_output\aw_element_tmp\wave4"


def imread_cn(path):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)


def tight_bbox(img, x1, y1, x2, y2, label, thresh=18):
    """在 (x1,y1,x2,y2) 区域内找与背景（区域中位色）差异 > thresh 的内容紧贴框。"""
    roi = img[y1:y2, x1:x2].astype(int)
    med = np.median(roi.reshape(-1, 3), axis=0)
    diff = np.abs(roi - med).sum(axis=2)
    mask = diff > thresh * 3
    if mask.sum() < 10:
        print(f"[{label}] 区域内几乎无内容像素 ({mask.sum()})，bbox 不可用")
        return None
    ys, xs = np.where(mask)
    bx1, by1, bx2, by2 = x1 + xs.min(), y1 + ys.min(), x1 + xs.max() + 1, y1 + ys.max() + 1
    # 诊断输出：内容占比、背景中位色
    print(f"[{label}] 内容像素 {mask.sum()}  背景 BGR={med.astype(int).tolist()}  "
          f"tight=({bx1},{by1})-({bx2},{by2})  size={bx2-bx1}x{by2-by1}")
    return (bx1, by1, bx2, by2)


def main():
    src_input = imread_cn(os.path.join(OUT, "src_search_input.png"))
    src_clear = imread_cn(os.path.join(OUT, "src_search_clear.png"))
    src_results = imread_cn(os.path.join(OUT, "src_search_results.png"))
    src_backfill = imread_cn(os.path.join(OUT, "src_search_backfill.png"))
    print(f"input shape={src_input.shape} clear={src_clear.shape} "
          f"results={src_results.shape} backfill={src_backfill.shape}")

    # 1) 返回箭头：语义节点 hit 区 (0,100,112,196)，箭头 glyph 应在其内
    tight_bbox(src_input, 0, 100, 112, 196, "BACK(input)")
    # 对照：backfill 页同区域
    tight_bbox(src_backfill, 0, 100, 112, 196, "BACK(backfill)")

    # 2) 搜索按钮：语义 desc=搜索 (579,117,688,163)，OCR 文本 (600,124,669,160)
    tight_bbox(src_input, 579, 110, 700, 170, "SUBMIT(input)")

    # 3) X 清空：results 页 OCR X (527,130,550,153)；clear/backfill 页同位分析
    tight_bbox(src_clear, 495, 110, 585, 170, "X(clear)")
    tight_bbox(src_results, 495, 110, 585, 170, "X(results)")
    tight_bbox(src_backfill, 495, 110, 585, 170, "X(backfill)")

    # 4) 空态文案：OCR (256,770,466,798)
    tight_bbox(src_results, 236, 750, 486, 818, "EMPTY(results)")


if __name__ == "__main__":
    main()
