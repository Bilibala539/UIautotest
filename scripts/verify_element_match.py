# -*- coding: utf-8 -*-
"""离线校验 image_ai/flutter/ 元素模板的 OpenCV 匹配质量（不碰真机）。

对每个元素模板，在 explorer 存档的整页截图中找它的来源页，跑与框架一致的
TM_CCOEFF_NORMED 匹配，报告最佳得分/位置/阈值判定。element 采集完成后先跑本脚本，
得分达标的元素才安排上真机点击验证。

用法：
    python scripts/verify_element_match.py            # 全量
    python scripts/verify_element_match.py -t 0.8     # 自定义阈值
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TPL_DIR = PROJECT_ROOT / "image_ai" / "flutter"
SRC_DIRS = [
    PROJECT_ROOT / "explorer_output" / "screenshots" / "swan",
    PROJECT_ROOT / "explorer_output" / "screenshots" / "swan_element_src",
    PROJECT_ROOT / "explorer_output" / "aw_element_tmp",
]


def imread_cn(path: Path):
    return cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)


def best_match(template, sources):
    """在所有候选整页图中匹配模板，返回 (得分, 位置, 源图路径)。"""
    best = (None, None, None)
    th, tw = template.shape[:2]
    for src in sources:
        page = imread_cn(src)
        if page is None:
            continue
        ph, pw = page.shape[:2]
        if ph < th or pw < tw:
            continue
        res = cv2.matchTemplate(page, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if best[0] is None or max_val > best[0]:
            best = (max_val, max_loc, src)
    return best


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--threshold", type=float, default=0.8,
                        help="判定阈值（与框架 find_image 默认一致）")
    args = parser.parse_args()

    sources = [p for d in SRC_DIRS if d.is_dir()
               for p in d.rglob("*.png") if "element" not in p.stem or "src" in str(d)]
    if not sources:
        print("❌ 没有可用的整页截图源（explorer_output/screenshots/swan*）")
        return 1

    templates = sorted(TPL_DIR.glob("*.png")) if TPL_DIR.is_dir() else []
    if not templates:
        print("❌ image_ai/flutter/ 下没有元素模板")
        return 1

    print(f"模板 {len(templates)} 个 | 源图 {len(sources)} 张 | 阈值 {args.threshold}")
    print("-" * 90)
    passed = 0
    for tpl_path in templates:
        tpl = imread_cn(tpl_path)
        if tpl is None:
            print(f"[跳过] {tpl_path.name}（读取失败）")
            continue
        score, loc, src = best_match(tpl, sources)
        if score is None:
            print(f"[失败] {tpl_path.name}（源图都小于模板，疑似整页截图尺寸不符）")
            continue
        ok = score >= args.threshold
        passed += ok
        mark = "✅" if ok else ("⚠️" if score >= args.threshold - 0.05 else "❌")
        print(f"{mark} {tpl_path.name:<40} 得分 {score:.3f} @ {loc}  ←  {src.name}")

    print("-" * 90)
    print(f"达标 {passed}/{len(templates)}（阈值 {args.threshold}；0.75~0.8 之间建议真机复验）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
