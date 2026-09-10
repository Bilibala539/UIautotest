# -*- coding: utf-8 -*-
"""Wave5 元素裁剪：按 OCR bbox + 像素分析从源图裁剪 10 张元素图到 image_ai/flutter/。

bbox 来源：
- PaddleOCR 文字框（analyze5.py 各页 ocr dump，紧贴文字 ±2px）
- 像素深色方块分析（平台行按钮 48x48，analyze5.py）
- 非白内容边界分析（DIY 上传卡，analyze5.py）
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from image.image_name_mapping import image_path  # noqa: E402

SRC = r"E:\UIAutotest\explorer_output\aw_element_tmp\wave5"
DRAFT = r"E:\UIAutotest\image_ai\flutter"

# (源图, 文件名, x1, y1, x2, y2)
CROPS = [
    # 所有角色页：「多选」文字按钮（OCR (627,890,686,923)，白底黑字）
    ("src_all_roles.png", "swan_所有角色页_多选按钮.png", 625, 888, 688, 925),
    # 角色编辑页：「选择」文字按钮（OCR (558,388,622,425)，深底白字）
    ("src_role_editor_top.png", "swan_角色编辑页_选择按钮.png", 556, 386, 624, 427),
    # 角色编辑页：「更多AI平台」通栏按钮文字（OCR (278,1060,442,1100)）
    ("src_role_editor_top.png", "swan_角色编辑页_更多AI平台按钮.png", 276, 1058, 444, 1102),
    # 角色编辑页：底部「完成」通栏按钮文字（补采 bottom2，OCR (323,1447,399,1492)；⛔ 不点击）
    ("src_role_editor_bottom2.png", "swan_角色编辑页_完成按钮.png", 321, 1445, 401, 1494),
    # AI形象页：「DIY形象」底部右半按钮（OCR (476,1527,587,1562)）
    ("src_ai_images.png", "swan_AI形象页_DIY形象按钮.png", 474, 1525, 589, 1564),
    # AI平台管理页：Qwen 行右侧 48x48 深色圆角方块（像素分析 (608,264)-(655,311)，8 行同构）
    ("src_ai_platform.png", "swan_AI平台管理页_平台行按钮.png", 606, 262, 658, 314),
    # AI平台管理页：顶栏「平台」标题（OCR (320,107,400,155)；region 断言用，避开底 tab 同名）
    ("src_ai_platform.png", "swan_AI平台管理页_顶栏平台标题.png", 318, 105, 402, 157),
    # AI历史页：顶栏「历史对话记录」标题行（OCR (252,110,469,150)）
    ("src_ai_history.png", "swan_AI历史页_标题行.png", 250, 108, 471, 152),
    # DIY形象页：「开始生成」通栏按钮文字（OCR (291,1183,429,1223)；⛔ 禁止点击）
    ("src_diy.png", "swan_DIY形象页_开始生成按钮.png", 289, 1181, 431, 1225),
    # DIY形象页：上传照片大虚线卡（非白内容 (92,310)-(615,668)；⛔ 不点击，不触发相册）
    ("src_diy.png", "swan_DIY形象页_上传照片卡.png", 90, 308, 618, 670),
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
