# -*- coding: utf-8 -*-
"""补采：角色编辑页更底部（完成按钮）。swipe_up x2 不够，追加 x4。

⛔ 完成按钮不点击。
用法：venv/Scripts/python.exe explorer_output/aw_element_tmp/wave5/capture5_editor2.py
前置：当前在首页·推荐 Tab（tab_recommend 可见）。
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")

from dotenv import load_dotenv  # noqa: E402

load_dotenv(r"E:\UIAutotest\.env.local")

from utils.aw.driver.flutter_driver import FlutterAndroidDriver  # noqa: E402
from utils.user import SwanUser  # noqa: E402
from utils.aw.business.swan import SwanBusiness as SB  # noqa: E402
from image.image_name_mapping import SWAN_HOME_AI_ROLE_SETTINGS  # noqa: E402

OUT = r"E:\UIAutotest\explorer_output\aw_element_tmp\wave5"
TOP_TAB_REGION = (0, 60, 720, 200)


def ocr_dump(aw, name: str, region=None) -> list:
    items = aw.ocr_scan_page(region=region)
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(f"{it['text']!r} conf={it['confidence']:.2f} bbox={it['bbox']}\n")
    print(f"[ocr] {name} ({len(items)} items)")
    return items


def main() -> None:
    user = SwanUser(driver=FlutterAndroidDriver())
    aw = user.aw
    assert aw.wait_accessibility(SB.KEY_TAB_ME, timeout=10), "不在首页"
    assert aw.click_text("AI", region=TOP_TAB_REGION), "点顶 Tab「AI」失败"
    time.sleep(1.5)
    assert aw.click_image(SWAN_HOME_AI_ROLE_SETTINGS, threshold=0.8, timeout=10), "进所有角色页失败"
    time.sleep(2.0)
    assert aw.click_text("添加更多AI角色"), "进角色编辑页失败"
    time.sleep(2.0)
    assert aw.text_exists("自定义设置", timeout=10), "未进入角色编辑页"

    # 追加滚动：共 swipe_up x4，每次后检查「完成」是否可见
    seen = False
    for i in range(4):
        aw.swipe_up()
        time.sleep(1.0)
        try:
            if aw.text_exists("完成", timeout=2):
                seen = True
                print(f"[ok] 完成按钮可见（swipe_up x{i + 3} 累计）")
                break
        except AssertionError:
            continue
    assert seen, "swipe_up x7 仍未见完成按钮"

    time.sleep(1.0)
    aw.take_screenshot(save_path=os.path.join(OUT, "src_role_editor_bottom2.png"))
    print("[shot] src_role_editor_bottom2.png")
    nodes = aw.dump_semantics()
    slim = [{"id": (n.get("resource_id") or "").split("/")[-1], "text": n.get("text"),
             "desc": n.get("content_desc"), "click": n.get("clickable"),
             "bounds": n.get("bounds")} for n in nodes]
    with open(os.path.join(OUT, "role_editor_bottom2_nodes.json"), "w", encoding="utf-8") as f:
        json.dump(slim, f, ensure_ascii=False, indent=1)
    ocr_dump(aw, "role_editor_bottom2_ocr.txt")
    # 滚回顶部（⛔ 不点完成）
    for _ in range(6):
        aw.swipe_down()
        time.sleep(0.6)
    print("[done] 补采完成，已滚回顶部")


if __name__ == "__main__":
    main()
