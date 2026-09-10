# -*- coding: utf-8 -*-
"""Wave2 元素裁剪：按探测得到的 bbox 从源图裁剪 12 张元素图到 image_ai/flutter/。

每个 bbox 来源：uiautomator 语义 dump / PaddleOCR 文字框 / 像素连通域 probe.py
（分析记录见 wave2/*_nodes.txt 与运行日志）。
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from image.image_name_mapping import image_path  # noqa: E402

SRC = r"E:\UIAutotest\explorer_output\aw_element_tmp\wave2"

# (源图, 文件名, x1, y1, x2, y2)
CROPS = [
    # P0 歌单详情页右上「⋮」更多按钮（glyph 657,96-673,136）
    ("src_playlist_detail.png", "swan_歌单详情页_更多按钮.png", 652, 91, 678, 141),
    # P0 歌单页右上新建歌单图标（glyph 625,100-681,156）
    ("src_playlist.png", "swan_歌单页_新建歌单按钮.png", 621, 96, 685, 160),
    # P1 歌单页左上返回箭头（glyph 49,108-75,149）
    ("src_playlist.png", "swan_歌单页_返回按钮.png", 45, 104, 79, 153),
    # P1 歌单页平台 Tab「SWAN」未选中态（从 QQ音乐 Tab 页截，text 53,234-139,262）
    ("src_playlist_qq.png", "swan_歌单页_SWAN平台Tab.png", 49, 230, 143, 266),
    # P1 歌单详情页「播放全部」行（▶图标 33,495-95,557 + 播放全部/0首歌 两行文案；
    #    ⚠️ 含"0首歌"计数，歌单加歌后需重截）
    ("src_playlist_detail.png", "swan_歌单详情页_播放全部.png", 29, 487, 240, 567),
    # P2 我喜欢页「播放全部」行（与歌单详情同模板分开截）
    ("src_favorite.png", "swan_我喜欢页_播放全部.png", 29, 487, 240, 567),
    # P2 播放历史页顶栏整条（返回箭头 37,108-63,149 + 标题 284,108-436,151）
    ("src_history.png", "swan_播放历史页_顶栏.png", 0, 102, 720, 158),
    # P2 播放历史页分类 Tab 条整条（歌曲…播客，text x29-637 y223-258）
    ("src_history.png", "swan_播放历史页_分类Tab条.png", 24, 218, 642, 263),
    # P2 切换设备弹层标题行（「切换设备」29,847-181,890；设备行 dynamic 不截）
    ("src_device_sheet.png", "swan_切换设备弹层_标题行.png", 0, 838, 720, 902),
    # P3 播放页右上设备切换图标（glyph 632,106-680,150）
    ("src_player.png", "swan_播放页_设备切换按钮.png", 628, 102, 684, 154),
    # P3 AI 对话页顶栏语音输入图标（glyph 446,129-499,183）
    ("src_ai_chat.png", "swan_AI对话页_语音按钮.png", 442, 125, 503, 187),
    # P3 AI 对话页底部输入框（EditText 64,1418-588,1510，含占位文案"发送消息.."）
    ("src_ai_chat.png", "swan_AI对话页_输入框.png", 64, 1418, 588, 1510),
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
