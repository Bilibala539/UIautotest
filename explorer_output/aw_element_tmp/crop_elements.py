# -*- coding: utf-8 -*-
"""Wave1 元素裁剪：按已验证的 bbox 从源图裁剪 14 张元素图到 image_ai/flutter/。

每个 bbox 来源：uiautomator 语义 dump / PaddleOCR 文字框 / 像素连通域+行列剖面分析
（分析过程见 aw_element_tmp/probe.py 等脚本的运行记录）。
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from image.image_name_mapping import image_path  # noqa: E402

SRC = r"E:\UIAutotest\explorer_output\aw_element_tmp"
DRAFT = r"E:\UIAutotest\image_ai\flutter"

# (源图, 文件名, x1, y1, x2, y2)
CROPS = [
    # P1 顶 Tab（未选中态：4 张取自推荐选中页，推荐取自音乐选中页）
    ("src_home_recommend.png", "swan_首页_音乐Tab按钮.png", 172, 101, 245, 145),
    ("src_home_recommend.png", "swan_首页_电台Tab按钮.png", 618, 101, 691, 145),
    ("src_home_recommend.png", "swan_首页_AITab按钮.png", 313, 105, 352, 137),
    ("src_home_recommend.png", "swan_首页_可视音箱Tab按钮.png", 419, 100, 556, 144),
    ("src_home_music.png", "swan_首页_推荐Tab按钮.png", 27, 101, 100, 144),
    # P2 搜索条（完整 pill：x32-687，音乐 y208-279 / 电台 y202-273）
    ("src_home_music.png", "swan_首页音乐Tab_搜索条.png", 31, 207, 688, 280),
    ("src_home_radio.png", "swan_首页电台Tab_搜索条.png", 31, 201, 688, 274),
    # P2 AI Tab 入口行（左 pill 文本按钮 / 右 pill 图标按钮）
    ("src_home_ai.png", "swan_首页AITab_添加角色入口.png", 106, 699, 507, 774),
    ("src_home_ai.png", "swan_首页AITab_角色设置入口.png", 521, 698, 616, 776),
    # P2 可视音箱未绑定提示（灰字提示行）
    ("src_home_vision.png", "swan_首页可视音箱Tab_未绑定提示.png", 143, 504, 575, 542),
    # P0 我的页右上角扫一扫图标（48x48）
    ("src_me.png", "swan_我的_扫一扫图标.png", 624, 214, 676, 266),
    # P3 资料编辑页右上角完成（注意不是 IME 键盘上的"完成"）
    ("src_profile_edit.png", "swan_资料编辑_完成按钮.png", 607, 108, 674, 152),
    # P3 头像弹层底部"取消"按钮
    ("src_avatar_popup.png", "swan_资料编辑_头像弹层取消.png", 321, 1476, 399, 1524),
    # P3 区号选择页"中国 +86"整行（含 +86 以区别于中国香港/澳门/台湾行首两字）
    ("src_area_code.png", "swan_区号选择_中国行.png", 14, 263, 650, 312),
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
