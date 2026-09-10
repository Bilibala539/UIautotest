# -*- coding: utf-8 -*-
"""aw-element Wave4 元素源图采集脚本（平台/搜索域）。

通过 AW 层（SwanUser/FlutterAndroidDriver）导航真机并截整页图，
保存到 explorer_output/aw_element_tmp/wave4/ 供裁剪与离线匹配校验。
用法：venv/Scripts/python.exe explorer_output/aw_element_tmp/wave4/capture4.py <stage>
stage: search | gate | platform | reset
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

OUT = r"E:\UIAutotest\explorer_output\aw_element_tmp\wave4"
os.makedirs(OUT, exist_ok=True)

TOP_TAB_REGION = (0, 60, 720, 200)   # 首页顶 Tab 行
TOPBAR_REGION = (0, 60, 720, 300)    # 搜索页/结果页顶栏（避开 T9 键盘"搜索"键 y>1150）
LEFT_SIDEBAR = (0, 200, 220, 1600)   # 平台页左侧分类栏


def make_user() -> SwanUser:
    return SwanUser(driver=FlutterAndroidDriver())


def shot(aw, name: str) -> None:
    path = os.path.join(OUT, name)
    aw.take_screenshot(save_path=path)
    print(f"[shot] {name}")


def dump_nodes(aw, name: str) -> None:
    """全量语义节点保存为 json（供离线定位裁剪框）。"""
    nodes = aw.dump_semantics()
    slim = []
    for n in nodes:
        slim.append({
            "id": (n.get("resource_id") or "").split("/")[-1],
            "text": n.get("text"),
            "desc": n.get("content_desc"),
            "click": n.get("clickable"),
            "bounds": n.get("bounds"),
        })
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(slim, f, ensure_ascii=False, indent=1)
    print(f"[dump] {name} ({len(slim)} nodes)")


def ocr_dump(aw, name: str, region=None) -> list:
    items = aw.ocr_scan_page(region=region)
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(f"{it['text']!r} conf={it['confidence']:.2f} bbox={it['bbox']}\n")
    print(f"[ocr] {name} ({len(items)} items)")
    return items


def at_home(aw, timeout: float = 10.0) -> None:
    assert aw.wait_accessibility(SB.KEY_TAB_ME, timeout=timeout), "不在首页（tab_me 未出现）"


def go_home_recommend(aw) -> None:
    """回到首页并切到推荐 Tab（跨会话持久，显式归一化）。

    注意：首页顶 Tab 行（推荐/音乐/电台…）只在首页存在；若当前在平台/设备等
    其他底部 Tab 页，必须先点底部 tab_recommend 回首页再点顶 Tab「推荐」。
    """
    if not aw.click_accessibility(SB.KEY_TAB_RECOMMEND):
        assert aw.wait_accessibility(SB.KEY_TAB_ME, timeout=8), "不在任何主页面（tab_me 未出现）"
    assert aw.wait_accessibility(SB.KEY_TAB_ME, timeout=8), "未回到首页"
    time.sleep(1.2)
    assert aw.click_text("推荐", region=TOP_TAB_REGION), "点顶 Tab「推荐」失败"
    time.sleep(1.5)


# =====================================================================
# stage search：搜索输入页（返回/搜索/清空X） + 搜索结果页（空态）
# =====================================================================
def stage_search() -> None:
    user = make_user()
    aw = user.aw
    at_home(aw)

    # 1) 进音乐 Tab，复位滚动，点搜索条进 /search
    assert aw.click_text("音乐", region=TOP_TAB_REGION), "点顶 Tab「音乐」失败"
    time.sleep(2.0)
    aw.swipe_down()
    aw.swipe_down()
    time.sleep(0.8)
    assert aw.click_text("跨平台搜索音乐"), "点音乐 Tab 搜索条失败"
    assert aw.text_exists("搜索歌曲或艺术家等", timeout=10), "未进入搜索输入页"
    time.sleep(1.0)

    # 2) 干净输入页源图（返回箭头 + 搜索按钮）
    dump_nodes(aw, "search_input_nodes.json")
    ocr_dump(aw, "search_input_ocr.txt", region=TOPBAR_REGION)
    shot(aw, "src_search_input.png")

    # 3) 聚焦输入框 → T9 键盘弹起 → adb 输入 abc → 截 X 清空按钮
    assert aw.click_text("搜索歌曲或艺术家等"), "点搜索框失败"
    time.sleep(1.5)
    assert aw.input_text("abc"), "输入 abc 失败"
    time.sleep(1.0)
    ocr_dump(aw, "search_clear_ocr.txt", region=TOPBAR_REGION)
    shot(aw, "src_search_clear.png")

    # 4) 点顶栏「搜索」提交（region 限定避开 T9 键盘的搜索键）→ 结果页空态
    assert aw.click_text("搜索", region=TOPBAR_REGION), "点顶栏搜索按钮失败"
    assert aw.text_exists("没有找到相关结果", timeout=10), "结果页空态文案未出现"
    time.sleep(1.0)
    dump_nodes(aw, "search_results_nodes.json")
    ocr_dump(aw, "search_results_ocr.txt")
    shot(aw, "src_search_results.png")

    # 5) press_back 回输入页（关键词回填，X 可见，无键盘）再补一张 X 源图
    aw.press_back()
    time.sleep(1.0)
    if aw.text_exists("搜索历史", timeout=5):
        ocr_dump(aw, "search_backfill_ocr.txt", region=TOPBAR_REGION)
        shot(aw, "src_search_backfill.png")

    # 6) 再 press_back 回首页音乐 Tab
    aw.press_back()
    time.sleep(1.5)
    print("[stage search] done，当前应在首页音乐 Tab")


# =====================================================================
# stage gate：授权门禁弹层 变体B（授权登录）/ 变体A（添加）
# ⛔ 只截图，主按钮绝不点击；press_back 关闭
# =====================================================================
def wait_gate_closed(aw, timeout: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not any((n.get("content_desc") == "纱罩") for n in aw.dump_semantics()):
            return True
        time.sleep(0.5)
    return False


def gate_open(aw) -> bool:
    return any((n.get("content_desc") == "纱罩") for n in aw.dump_semantics())


def find_and_click(aw, text: str, max_swipe: int = 0, region=None) -> bool:
    """OCR 找文字并点击（click_text），找不到则下滑重试（music/radio tab 内容可滚动）。"""
    for i in range(max_swipe + 1):
        if aw.click_text(text, timeout=4, region=region):
            return True
        if i < max_swipe:
            aw.swipe_up()
            time.sleep(1.0)
    return False


def stage_gate() -> None:
    user = make_user()
    aw = user.aw
    at_home(aw)

    # --- 变体 B：音乐 Tab 平台区块「QQ音乐」→ 授权登录 ---
    assert aw.click_text("音乐", region=TOP_TAB_REGION), "点顶 Tab「音乐」失败"
    time.sleep(2.0)
    aw.swipe_down()
    aw.swipe_down()
    time.sleep(0.8)
    assert find_and_click(aw, "QQ音乐", max_swipe=3), "未找到 QQ音乐 平台区块标题"
    time.sleep(2.0)
    assert gate_open(aw), "变体B 门禁未弹出（desc=纱罩 不在语义树）"
    dump_nodes(aw, "auth_login_nodes.json")
    ocr_dump(aw, "auth_login_ocr.txt")
    shot(aw, "src_auth_login.png")
    aw.press_back()
    time.sleep(1.0)
    assert wait_gate_closed(aw), "变体B 门禁 press_back 后未关闭"
    print("[gate B] 授权登录弹层已截图并关闭")

    # --- 变体 A：电台 Tab 分组标题「全国电台」→ 添加 ---
    assert aw.click_text("电台", region=TOP_TAB_REGION), "点顶 Tab「电台」失败"
    time.sleep(2.0)
    aw.swipe_down()
    aw.swipe_down()
    time.sleep(0.8)
    assert find_and_click(aw, "全国电台", max_swipe=3), "未找到 全国电台 分组标题"
    time.sleep(2.0)
    assert gate_open(aw), "变体A 门禁未弹出"
    dump_nodes(aw, "auth_add_nodes.json")
    ocr_dump(aw, "auth_add_ocr.txt")
    shot(aw, "src_auth_add.png")
    aw.press_back()
    time.sleep(1.0)
    assert wait_gate_closed(aw), "变体A 门禁 press_back 后未关闭"
    print("[gate A] 添加弹层已截图并关闭，当前在首页电台 Tab")


# =====================================================================
# stage platform：平台页·电台分类行右侧圆形箭头（⛔ 不点击）
# =====================================================================
def stage_platform() -> None:
    user = make_user()
    aw = user.aw
    at_home(aw)

    assert aw.click_accessibility(SB.KEY_TAB_PLATFORM), "点底部「平台」Tab 失败"
    assert aw.wait_accessibility(SB.KEY_PLATFORM_PAGE, timeout=10), "未进入平台页"
    time.sleep(1.5)

    # 左侧分类跨会话持久：确认当前分类（OCR 左侧栏）
    ocr_dump(aw, "platform_sidebar_ocr.txt", region=LEFT_SIDEBAR)
    # 若不在「电台」分类则切换
    if not aw.text_exists("电台", timeout=3, region=LEFT_SIDEBAR):
        print("[warn] 左侧栏未见「电台」分类，dump 全页 OCR 人工确认")
    dump_nodes(aw, "platform_nodes.json")
    shot(aw, "src_platform_radio.png")
    print("[stage platform] done（未点击任何电台行/箭头），当前在平台页")


# =====================================================================
# stage reset：平台页切回音乐分类 → 回首页·推荐 Tab
# =====================================================================
def stage_reset() -> None:
    user = make_user()
    aw = user.aw
    if aw.wait_accessibility(SB.KEY_PLATFORM_PAGE, timeout=3):
        # 切回音乐分类（左侧栏）
        if aw.click_text("音乐", timeout=4, region=LEFT_SIDEBAR):
            time.sleep(1.5)
            print("[reset] 平台页左侧分类已切回音乐")
        else:
            print("[warn] 未找到左侧「音乐」分类，请人工确认")
    go_home_recommend(aw)
    shot(aw, "final_state.png")
    print("[reset] done，已复位到首页·推荐 Tab")


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage == "search":
        stage_search()
    elif stage == "gate":
        stage_gate()
    elif stage == "platform":
        stage_platform()
    elif stage == "reset":
        stage_reset()
    else:
        raise SystemExit(f"未知 stage: {stage!r}（可选 search / gate / platform / reset）")
