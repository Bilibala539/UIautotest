# -*- coding: utf-8 -*-
"""aw-element Wave5 元素源图采集脚本（AI/Vision/视频域）。

通过 AW 层（SwanUser/FlutterAndroidDriver）导航真机并截整页图，
保存到 explorer_output/aw_element_tmp/wave5/ 供裁剪与离线匹配校验。
用法：venv/Scripts/python.exe explorer_output/aw_element_tmp/wave5/capture5.py <stage>
stage: roles | editor | images | platform | history | reset

⛔ 红线：
- DIY形象页「开始生成」「充值」「上传照片」一律不点击（付费/拉起相册）
- AI 平台管理页平台行右侧按钮不点击（弹添加门禁）；「添加」绝不点
- 角色编辑页「完成」不点击（创建角色）；所有角色页多选态「全选」「删除」不点
- 实时通话入口不进入；禁止 tap 坐标
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
os.makedirs(OUT, exist_ok=True)

TOP_TAB_REGION = (0, 60, 720, 200)    # 首页顶 Tab 行
TOPBAR_REGION = (0, 60, 720, 190)     # 二级页顶栏（标题断言/OCR）


def make_user() -> SwanUser:
    return SwanUser(driver=FlutterAndroidDriver())


def shot(aw, name: str) -> None:
    path = os.path.join(OUT, name)
    aw.take_screenshot(save_path=path)
    print(f"[shot] {name}")


def dump_nodes(aw, name: str) -> None:
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


def on_text(aw, text: str, timeout: float = 3.0) -> bool:
    """text_exists 的非断言版（找不到返回 False 而不是抛异常）。"""
    try:
        return aw.text_exists(text, timeout=timeout)
    except AssertionError:
        return False


def at_home(aw, timeout: float = 10.0) -> None:
    assert aw.wait_accessibility(SB.KEY_TAB_ME, timeout=timeout), "不在首页（tab_me 未出现）"


def go_ai_tab(aw) -> None:
    """回首页并切到 AI 顶 Tab（跨会话持久，显式归一化）。"""
    if not aw.click_accessibility(SB.KEY_TAB_RECOMMEND):
        assert aw.wait_accessibility(SB.KEY_TAB_ME, timeout=8), "不在任何主页面"
    assert aw.wait_accessibility(SB.KEY_TAB_ME, timeout=8), "未回到首页"
    time.sleep(1.2)
    assert aw.click_text("AI", region=TOP_TAB_REGION), "点顶 Tab「AI」失败"
    time.sleep(1.5)


# =====================================================================
# stage roles：首页 AI Tab → 所有角色页
# =====================================================================
def stage_roles() -> None:
    user = make_user()
    aw = user.aw
    at_home(aw)
    go_ai_tab(aw)
    shot(aw, "src_home_ai.png")

    assert aw.click_image(SWAN_HOME_AI_ROLE_SETTINGS, threshold=0.8, timeout=10), \
        "点「AI 角色设置」图标失败"
    time.sleep(2.0)
    assert aw.text_exists("所有角色", timeout=10), "未进入所有角色页"
    shot(aw, "src_all_roles.png")
    dump_nodes(aw, "all_roles_nodes.json")
    ocr_dump(aw, "all_roles_ocr.txt")
    print("[stage roles] done，当前在所有角色页")


# =====================================================================
# stage editor：所有角色页 → 角色编辑页（上半屏 + swipe_up x2 下半屏）
# ⛔ 「完成」不点击
# =====================================================================
def stage_editor() -> None:
    user = make_user()
    aw = user.aw
    assert aw.text_exists("所有角色", timeout=8), "不在所有角色页（请先跑 roles）"
    assert aw.click_text("添加更多AI角色"), "点「添加更多AI角色」失败"
    time.sleep(2.0)
    assert aw.text_exists("自定义设置", timeout=10), "未进入角色编辑页"
    time.sleep(1.0)
    shot(aw, "src_role_editor_top.png")
    dump_nodes(aw, "role_editor_top_nodes.json")
    ocr_dump(aw, "role_editor_top_ocr.txt")

    # 表单两屏长：swipe_up x2 看下半屏（语音选择/昵称/完成）
    aw.swipe_up()
    time.sleep(1.0)
    aw.swipe_up()
    time.sleep(1.2)
    assert aw.text_exists("语音选择", timeout=8), "swipe_up x2 后未见语音选择（滚动异常）"
    shot(aw, "src_role_editor_bottom.png")
    dump_nodes(aw, "role_editor_bottom_nodes.json")
    ocr_dump(aw, "role_editor_bottom_ocr.txt")

    # 滚回顶部（供后续 images/platform stage 用），⛔ 不点完成
    aw.swipe_down()
    time.sleep(0.8)
    aw.swipe_down()
    time.sleep(1.0)
    print("[stage editor] done（⛔ 完成按钮未点击），当前在角色编辑页顶部")


# =====================================================================
# stage images：角色编辑页 → AI形象页 → DIY形象页（⛔ 只截图不点击）
# =====================================================================
def stage_images() -> None:
    user = make_user()
    aw = user.aw
    assert aw.text_exists("自定义设置", timeout=8), "不在角色编辑页（请先跑 editor）"

    assert aw.click_text("选择", timeout=8), "点「选择」（形象生成区）失败"
    time.sleep(2.0)
    assert aw.text_exists("DIY形象", timeout=10), "未进入 AI 形象页（未见 DIY形象 按钮）"
    shot(aw, "src_ai_images.png")
    dump_nodes(aw, "ai_images_nodes.json")
    ocr_dump(aw, "ai_images_ocr.txt")

    assert aw.click_text("DIY形象"), "点「DIY形象」按钮失败"
    time.sleep(2.0)
    assert aw.text_exists("0.2惠币", timeout=10), "未进入 DIY 形象页（未见付费提示）"
    shot(aw, "src_diy.png")
    dump_nodes(aw, "diy_nodes.json")
    ocr_dump(aw, "diy_ocr.txt")
    # ⛔ 开始生成/充值/上传照片 均不点击；press_back 返回
    aw.press_back()
    time.sleep(1.5)
    assert aw.text_exists("DIY形象", timeout=8), "press_back 后未回 AI 形象页"
    print("[stage images] done（⛔ DIY 页付费按钮未点击），当前在 AI 形象页")


# =====================================================================
# stage platform：AI形象页 →(back)→ 角色编辑页 → 更多AI平台 → AI 平台管理页
# ⛔ 平台行右侧按钮不点击（弹添加门禁）
# =====================================================================
def stage_platform() -> None:
    user = make_user()
    aw = user.aw
    # 从 AI 形象页回到角色编辑页（若当前已在编辑页也可）
    if on_text(aw, "自定义设置"):
        pass
    elif on_text(aw, "DIY形象"):
        aw.press_back()
        time.sleep(1.5)
        assert aw.text_exists("自定义设置", timeout=8), "回不到角色编辑页"
    else:
        raise SystemExit("不在 AI 形象页/角色编辑页（请先跑 images）")

    assert aw.click_text("更多AI平台"), "点「更多AI平台」失败"
    time.sleep(2.0)
    # 标题「平台」需 region 限定顶栏（与底部 tab「平台」同名）
    assert aw.text_exists("平台", timeout=8, region=TOPBAR_REGION), "未进入 AI 平台管理页"
    assert aw.text_exists("Qwen", timeout=8), "平台列表未渲染（未见 Qwen 行）"
    shot(aw, "src_ai_platform.png")
    dump_nodes(aw, "ai_platform_nodes.json")
    ocr_dump(aw, "ai_platform_ocr.txt")
    print("[stage platform] done（⛔ 平台行按钮未点击），当前在 AI 平台管理页")


# =====================================================================
# stage history：AI 平台管理页 →(back x3)→ AI Tab → 历史对话记录标题行
# ⚠️ 点标题行本身，不点记录行（落点不同）
# =====================================================================
def stage_history() -> None:
    user = make_user()
    aw = user.aw
    # 逐级 press_back：平台管理页→角色编辑页→所有角色页→AI Tab
    for _ in range(3):
        aw.press_back()
        time.sleep(1.5)
    at_home(aw)
    go_ai_tab(aw)
    time.sleep(1.0)

    # ⚠️ 点区块标题行「历史对话记录」本身（可点 ImageView），不是记录行
    assert aw.click_text("历史对话记录"), "点「历史对话记录」标题行失败"
    time.sleep(2.0)
    assert aw.text_exists("历史对话记录", timeout=10, region=TOPBAR_REGION), \
        "未进入 AI 历史页（顶栏无标题；可能误点记录行）"
    shot(aw, "src_ai_history.png")
    dump_nodes(aw, "ai_history_nodes.json")
    ocr_dump(aw, "ai_history_ocr.txt")
    aw.press_back()
    time.sleep(1.5)
    print("[stage history] done，已返回 AI Tab")


# =====================================================================
# stage reset：回首页·推荐 Tab
# =====================================================================
def stage_reset() -> None:
    user = make_user()
    aw = user.aw
    if not aw.click_accessibility(SB.KEY_TAB_RECOMMEND):
        assert aw.wait_accessibility(SB.KEY_TAB_ME, timeout=8), "不在任何主页面"
    assert aw.wait_accessibility(SB.KEY_TAB_ME, timeout=8), "未回到首页"
    time.sleep(1.2)
    assert aw.click_text("推荐", region=TOP_TAB_REGION), "点顶 Tab「推荐」失败"
    time.sleep(1.5)
    shot(aw, "final_state.png")
    print("[reset] done，已复位到首页·推荐 Tab")


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    stages = {
        "roles": stage_roles,
        "editor": stage_editor,
        "images": stage_images,
        "platform": stage_platform,
        "history": stage_history,
        "reset": stage_reset,
    }
    if stage not in stages:
        raise SystemExit(f"未知 stage: {stage!r}（可选 {' / '.join(stages)}）")
    stages[stage]()
