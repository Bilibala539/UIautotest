# -*- coding: utf-8 -*-
"""aw-element Wave1 元素源图采集脚本。

通过 AW 层（SwanUser/FlutterAndroidDriver）导航真机并截整页图，
保存到 explorer_output/aw_element_tmp/ 供裁剪与离线匹配校验。
用法：venv/Scripts/python.exe explorer_output/aw_element_tmp/capture.py <stage>
stage: home_tabs | me_page
"""
from __future__ import annotations

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

OUT = r"E:\UIAutotest\explorer_output\aw_element_tmp"
os.makedirs(OUT, exist_ok=True)

TOP_TAB_REGION = (0, 60, 720, 200)  # 顶 Tab 行（runtime_experience: y≈121）


def make_user() -> SwanUser:
    return SwanUser(driver=FlutterAndroidDriver())


def shot(aw, name: str) -> None:
    path = os.path.join(OUT, name)
    aw.take_screenshot(save_path=path)
    print(f"[shot] {name}")


def dump_top_nodes(aw, label: str, y_max: int = 260) -> None:
    """打印屏幕上部语义节点（辅助精确定位裁剪框）。"""
    print(f"--- nodes y<{y_max} @ {label} ---")
    for n in aw.dump_semantics():
        b = n.get("bounds")
        if not b:
            continue
        x1, y1, x2, y2 = b
        if y2 <= y_max:
            rid = (n.get("resource_id") or "").split("/")[-1]
            print(f"  id={rid!r} text={n.get('text')!r} desc={n.get('content_desc')!r} "
                  f"click={n.get('clickable')} box=({x1},{y1})-({x2},{y2})")


def stage_home_tabs() -> None:
    user = make_user()
    aw = user.aw
    assert aw.wait_accessibility(SB.KEY_TAB_ME, timeout=10), "不在首页（tab_me 未出现）"
    time.sleep(1.0)

    # 1) 显式点「推荐」顶 Tab（选择跨登出持久，先归一化），截推荐 Tab 选中态源图
    assert aw.click_text("推荐", region=TOP_TAB_REGION), "点顶 Tab「推荐」失败"
    time.sleep(1.5)
    dump_top_nodes(aw, "home_recommend")
    shot(aw, "src_home_recommend.png")

    # 2) 音乐 Tab：截「推荐未选中态 + 音乐搜索条」
    assert aw.click_text("音乐", region=TOP_TAB_REGION), "点顶 Tab「音乐」失败"
    time.sleep(2.0)
    dump_top_nodes(aw, "home_music")
    shot(aw, "src_home_music.png")

    # 3) 电台 Tab
    assert aw.click_text("电台", region=TOP_TAB_REGION), "点顶 Tab「电台」失败"
    time.sleep(2.0)
    shot(aw, "src_home_radio.png")

    # 4) AI Tab（页内 y≈737 也有"AI"，region 限定顶栏）
    assert aw.click_text("AI", region=TOP_TAB_REGION), "点顶 Tab「AI」失败"
    time.sleep(2.0)
    shot(aw, "src_home_ai.png")

    # 5) 可视音箱 Tab
    assert aw.click_text("可视音箱", region=TOP_TAB_REGION), "点顶 Tab「可视音箱」失败"
    time.sleep(2.0)
    shot(aw, "src_home_vision.png")

    print("[stage home_tabs] done，当前停在首页·可视音箱 Tab")


def stage_me_page() -> None:
    user = make_user()
    aw = user.aw
    assert aw.wait_accessibility(SB.KEY_TAB_ME, timeout=10), "不在首页（tab_me 未出现）"

    # 我的页：右上角扫一扫图标
    assert aw.click_accessibility(SB.KEY_TAB_ME), "点底部「我的」失败"
    time.sleep(1.5)
    shot(aw, "src_me.png")

    # 个人信息页
    assert aw.click_accessibility(SB.KEY_ME_PROFILE_ENTRY), "点账号入口失败"
    assert aw.wait_accessibility(SB.KEY_PERSON_INFO_PAGE, timeout=10), "未进入个人信息页"
    time.sleep(1.0)
    shot(aw, "src_person_info.png")

    # 头像弹层（点「头像」行 → 弹层 → 截图 → OCR「取消」关闭）
    assert aw.click_text("头像"), "点「头像」行失败"
    time.sleep(1.5)
    shot(aw, "src_avatar_popup.png")
    assert aw.click_text("取消"), "点弹层「取消」失败"
    time.sleep(1.0)

    # 昵称 → 资料编辑页（完成按钮）
    assert aw.click_text("昵称"), "点「昵称」行失败"
    time.sleep(2.0)
    shot(aw, "src_profile_edit.png")
    aw.press_back()  # 收键盘
    time.sleep(0.8)
    aw.press_back()  # 返回个人信息页
    time.sleep(1.0)
    print("[stage me_page] done，当前停在个人信息页")


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage == "home_tabs":
        stage_home_tabs()
    elif stage == "me_page":
        stage_me_page()
    else:
        raise SystemExit(f"未知 stage: {stage!r}（可选 home_tabs / me_page）")
