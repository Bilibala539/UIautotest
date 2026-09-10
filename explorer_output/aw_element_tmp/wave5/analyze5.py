# -*- coding: utf-8 -*-
"""Wave5 像素分析：平台行按钮方块 / DIY 上传卡虚线边界 / 各文字按钮区域留白检查。"""
from __future__ import annotations

import cv2
import numpy as np

SRC = r"E:\UIAutotest\explorer_output\aw_element_tmp\wave5"


def imread_cn(path: str):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)


def analyze_platform_btn() -> None:
    """Qwen 行 [0,216,720,392] 内找深色圆角方块（行右侧）。"""
    img = imread_cn(SRC + r"\src_ai_platform.png")
    row = img[216:392, 500:720]
    gray = cv2.cvtColor(row, cv2.COLOR_BGR2GRAY)
    dark = (gray < 100).astype(np.uint8)
    ys, xs = np.nonzero(dark)
    if len(xs) == 0:
        print("[platform] 未找到深色像素")
        return
    x1, x2 = xs.min() + 500, xs.max() + 500
    y1, y2 = ys.min() + 216, ys.max() + 216
    print(f"[platform] Qwen 行深色方块 bbox=({x1},{y1})-({x2},{y2})  尺寸 {x2-x1+1}x{y2-y1+1}")
    # 每行Darkness 投影验证方块边界
    col_dark = dark.sum(axis=0)
    row_dark = dark.sum(axis=1)
    print(f"[platform] 列投影起止: x {np.nonzero(col_dark)[0].min()+500}~{np.nonzero(col_dark)[0].max()+500}")
    print(f"[platform] 行投影起止: y {np.nonzero(row_dark)[0].min()+216}~{np.nonzero(row_dark)[0].max()+216}")
    # 检查其他行是否同构（取 DeepSeek 行 y445 附近同 x 区域中心亮度）
    for name, cy in [("DeepSeek", 480), ("Kimi", 817), ("腾讯混元", 1522)]:
        patch = gray = None
        patch = cv2.cvtColor(img[cy - 40:cy + 40, x1:x2], cv2.COLOR_BGR2GRAY)
        print(f"[platform] {name} 行同位置区域均值={patch.mean():.0f}（<100 说明同为深色方块）")


def analyze_diy_card() -> None:
    """DIY 页找上传卡虚线边界：虚线为灰色，背景白。"""
    img = imread_cn(SRC + r"\src_diy.png")
    region = img[300:750, 0:720]  # 上传照片文本 y423-460 周边
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    nonwhite = (gray < 200).astype(np.uint8)
    ys, xs = np.nonzero(nonwhite)
    print(f"[diy] 非白内容 bbox=({xs.min()},{ys.min()+300})-({xs.max()},{ys.max()+300})")
    # 行投影找虚线上下边
    rowsum = nonwhite.sum(axis=1)
    edges = [i + 300 for i, v in enumerate(rowsum) if v > 30]
    print(f"[diy] 行密度>30 的 y: {edges[:5]}...{edges[-5:] if len(edges)>5 else edges}")


def check_text_padding() -> None:
    """各文字按钮 OCR 框周边留白检查（确认裁剪框附近没有其他元素干扰）。"""
    checks = [
        ("src_all_roles.png", "多选", (627, 890, 686, 923)),
        ("src_role_editor_top.png", "选择", (558, 388, 622, 425)),
        ("src_role_editor_top.png", "更多AI平台", (278, 1060, 442, 1100)),
        ("src_role_editor_bottom2.png", "完成", (323, 1447, 399, 1492)),
        ("src_ai_images.png", "DIY形象", (476, 1527, 587, 1562)),
        ("src_diy.png", "开始生成", (291, 1183, 429, 1223)),
        ("src_ai_platform.png", "平台标题", (320, 107, 400, 155)),
        ("src_ai_history.png", "历史对话记录", (252, 110, 469, 150)),
    ]
    for src, name, (x1, y1, x2, y2) in checks:
        img = imread_cn(SRC + "\\" + src)
        pad = 12
        box = img[max(y1 - pad, 0):y2 + pad, max(x1 - pad, 0):x2 + pad]
        gray = cv2.cvtColor(box, cv2.COLOR_BGR2GRAY)
        inner = gray[pad:-pad, pad:-pad] if pad else gray
        print(f"[{name}] {src} 框内均值={inner.mean():.0f} 标准差={inner.std():.0f} "
              f"外圈均值={gray.mean():.0f}  框外沿尺寸={box.shape[1]}x{box.shape[0]}")


if __name__ == "__main__":
    analyze_platform_btn()
    analyze_diy_card()
    check_text_padding()
