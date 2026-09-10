# -*- coding: utf-8 -*-
"""Wave4 元素裁剪：按像素分析 bbox 从源图裁剪 7 张元素图到 image_ai/flutter/。

bbox 来源：
- 语义 dump 节点框（授权门禁主按钮 pill / 搜索页顶栏节点）
- PaddleOCR 文字框（空态文案）
- 像素中位色差分析（返回箭头 glyph / 搜索按钮文字 / X 清空 / 电台行圆形箭头）
分析过程见 analyze4.py 运行记录与 wave4/*.json / *.txt。
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from image.image_name_mapping import image_path  # noqa: E402

SRC = r"E:\UIAutotest\explorer_output\aw_element_tmp\wave4"
DRAFT = r"E:\UIAutotest\image_ai\flutter"

# (源图, 文件名, x1, y1, x2, y2)
CROPS = [
    # 搜索输入页：返回箭头 glyph（语义 hit 区 (0,100,112,196) 内像素分析 tight (42,124)-(60,157)）
    ("src_search_input.png", "swan_搜索输入页_返回按钮.png", 40, 122, 62, 159),
    # 搜索输入页：顶栏「搜索」文字按钮（desc=搜索 节点 (579,117,688,163)，文字 tight (604,126)-(666,157)）
    ("src_search_input.png", "swan_搜索输入页_搜索按钮.png", 602, 124, 668, 159),
    # 搜索输入页：输入 abc 后框内 X 清空（键盘弹起态源图，glyph tight (529,130)-(549,150)）
    ("src_search_clear.png", "swan_搜索输入页_清空按钮.png", 527, 128, 551, 152),
    # 搜索结果页：空态文案（OCR tight (255,770)-(464,796)）
    ("src_search_results.png", "swan_搜索结果页_空态文案.png", 253, 768, 466, 798),
    # 授权门禁弹层 变体B 主按钮（语义节点 (216,1426,504,1518)，黑色 pill+白字，pill 即节点框）
    ("src_auth_login.png", "swan_授权门禁弹层_授权登录按钮.png", 216, 1426, 504, 1518),
    # 授权门禁弹层 变体A 主按钮（语义节点 (216,1290,504,1382)）
    ("src_auth_add.png", "swan_授权门禁弹层_添加按钮.png", 216, 1290, 504, 1382),
    # 平台页·电台分类行右侧圆形箭头（全国电台行 (124,492,720,656) 右侧，48x48 图标）
    ("src_platform_radio.png", "swan_平台_电台行箭头.png", 604, 538, 656, 590),
]


def imread_cn(path: str):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)


def imwrite_cn(path: str, img) -> None:
    ext = os.path.splitext(path)[1]
    ok, buf = cv2.imencode(ext, img)
    assert ok, f"编码失败: {path}"
    buf.tofile(path)


def validate(img, name: str) -> list[str]:
    """规范第 8 节截取后检查（4 项）。"""
    errors = []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if np.std(gray) < 5:
        errors.append("疑似空白（灰度标准差<5）")
    if np.mean(gray) < 5:
        errors.append("疑似全黑")
    if np.mean(gray) > 250:
        errors.append("疑似全白")
    b, g, r = img[:, :, 0].astype(int), img[:, :, 1].astype(int), img[:, :, 2].astype(int)
    red = ((r > 200) & (g < 160) & (b < 170) & (r - g > 40)).sum()
    if red > 0:
        errors.append(f"残留 {red} 个红色角标像素")
    h, w = img.shape[:2]
    if w < 10 or h < 10:
        errors.append(f"尺寸过小 {w}x{h}")
    return errors


def main() -> int:
    os.makedirs(DRAFT, exist_ok=True)
    failed = 0
    for src_name, out_name, x1, y1, x2, y2 in CROPS:
        img = imread_cn(os.path.join(SRC, src_name))
        assert img is not None, f"源图读取失败: {src_name}"
        crop = img[y1:y2, x1:x2]
        out_path = image_path(out_name, platform="flutter", draft=True)
        imwrite_cn(out_path, crop)
        errors = validate(crop, out_name)
        mark = "OK " if not errors else "BAD"
        if errors:
            failed += 1
        print(f"[{mark}] {out_name}  {x2-x1}x{y2-y1}  <- {src_name}"
              + ("" if not errors else "  " + "; ".join(errors)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
