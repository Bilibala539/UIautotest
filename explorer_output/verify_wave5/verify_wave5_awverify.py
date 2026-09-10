# -*- coding: utf-8 -*-
"""Wave 5（AI/Vision/视频域）元素图真机验证 + 点击反应验证（aw-verify，2026-09-10）。

验证 10 张暂存图（image_ai/flutter/）的存在性，其中 4 个可点击项做点击反应验证：
  1. SWAN_ALL_ROLES_MULTISELECT   点击 → 多选态（取消/全选/删除出现，多选消失），点取消还原
  2. SWAN_ROLE_EDITOR_SELECT      点击 → 进 AI 形象页，press_back 还原
  3. SWAN_ROLE_EDITOR_MORE_PLATFORM 点击 → 进 AI 平台管理页，press_back 还原
  4. SWAN_ROLE_IMAGES_DIY_BTN     点击 → 进 DIY 形象页，press_back 还原
⛔ 红线：SWAN_ROLE_EDITOR_DONE / SWAN_DIY_GENERATE_BTN / SWAN_DIY_UPLOAD_CARD /
   SWAN_AI_PLATFORM_ROW_BTN 只做存在性断言，绝不点击。

用法：
    cd E:/UIAutotest
    set PYTHONIOENCODING=utf-8
    venv/Scripts/python.exe explorer_output/verify_wave5/verify_wave5_awverify.py
前置：App 在首页·推荐 Tab，已登录。
"""
from __future__ import annotations

import logging
import os
import sys
import time

sys.path.insert(0, r"E:\UIAutotest")
os.environ.setdefault("PLATFORM", "flutter")
os.environ.setdefault("ANDROID_DEVICE_SERIAL", "c0614b6a")

from utils.aw.driver.flutter_driver import FlutterAndroidDriver  # noqa: E402
from utils.user import SwanUser  # noqa: E402
from image.image_name_mapping import (  # noqa: E402
    SWAN_HOME_AI_ROLE_SETTINGS,
    SWAN_ALL_ROLES_MULTISELECT,
    SWAN_ROLE_EDITOR_SELECT,
    SWAN_ROLE_EDITOR_MORE_PLATFORM,
    SWAN_ROLE_EDITOR_DONE,
    SWAN_ROLE_IMAGES_DIY_BTN,
    SWAN_DIY_GENERATE_BTN,
    SWAN_DIY_UPLOAD_CARD,
    SWAN_AI_PLATFORM_ROW_BTN,
    SWAN_AI_PLATFORM_TITLE,
    SWAN_AI_HISTORY_TITLE,
)

logging.getLogger("ppocr").setLevel(logging.WARNING)
logging.getLogger("paddle").setLevel(logging.WARNING)
_root = logging.getLogger()
_root.setLevel(logging.INFO)
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
_root.addHandler(_handler)
log = logging.getLogger("wave5_awverify")

SCREEN_W = 720
TOP_TAB_REGION = (0, 60, SCREEN_W, 200)
TOPBAR_REGION = (0, 60, SCREEN_W, 190)

RESULTS: dict[str, str] = {}


def verify_image(name: str, constant: str, region=None) -> bool:
    pos = aw.find_image(constant, threshold=0.8, timeout=8, region=region)
    if pos:
        RESULTS[name] = "存在断言通过(0.8)"
        log.info(f"[通过] {name} 存在 @ {pos}")
        return True
    log.warning(f"[重试] {name} 0.8 未命中，降阈值 0.7 重试")
    pos = aw.find_image(constant, threshold=0.7, timeout=5, region=region)
    if pos:
        RESULTS[name] = "存在断言降阈值通过(0.7)"
        log.info(f"[降阈值通过] {name} @ {pos}")
        return True
    RESULTS[name] = "失败"
    log.error(f"[失败] {name} 0.7 仍未命中")
    return False


def shot(step: str) -> None:
    aw.screenshot_for_explore(f"wave5_{step}.png", subdir="verify_wave5")
    time.sleep(0.3)


def on_text(text: str, timeout: float = 3.0, region=None) -> bool:
    try:
        return bool(aw.text_exists(text, timeout=timeout, region=region))
    except AssertionError:
        return False


def back_to_home(presses: int = 4) -> None:
    for _ in range(presses):
        if aw.accessibility_exists("tab_me"):
            return
        aw.press_back()
        time.sleep(1.5)
    assert aw.accessibility_exists("tab_me"), "未能回到首页（tab_me 不可见）"


# =====================================================================
driver = FlutterAndroidDriver(serial="c0614b6a")
user = SwanUser(driver=driver)
aw = user.aw

log.info("=== 0. 确认在首页 ===")
assert aw.wait_accessibility("tab_me", timeout=15), "不在首页，请先人工复位"
aw.click_text("AI", region=TOP_TAB_REGION)
time.sleep(1.5)
shot("00_home_ai")

log.info("=== 1. 所有角色页：多选按钮 存在 + 点击反应（进入/退出多选态）===")
assert aw.click_image(SWAN_HOME_AI_ROLE_SETTINGS, threshold=0.8, timeout=10), "进所有角色页失败"
time.sleep(2.0)
assert on_text("所有角色", 10), "未进入所有角色页"
shot("01_all_roles")
assert verify_image("SWAN_ALL_ROLES_MULTISELECT", SWAN_ALL_ROLES_MULTISELECT), "多选按钮图未命中"
assert aw.click_image(SWAN_ALL_ROLES_MULTISELECT, threshold=0.8, timeout=8), "点击多选按钮失败"
time.sleep(1.5)
shot("02_multiselect_on")
assert on_text("取消", 5), "多选态未出现「取消」"
assert on_text("全选", 5), "多选态未出现「全选」"
assert on_text("删除", 5), "多选态未出现「删除」"
assert not on_text("多选", 1.5), "多选态下「多选」按钮应已消失"
log.info("[通过] 多选态确认：取消/全选/删除 出现，多选消失")
assert aw.click_text("取消", timeout=8), "点击取消退出多选态失败"
time.sleep(1.5)
shot("03_multiselect_off")
assert on_text("多选", 5), "退出多选态后「多选」按钮未还原"
assert not on_text("全选", 1.5), "退出多选态后「全选」应消失"
log.info("[通过] 退出多选态还原：多选 回归，全选 消失")
RESULTS["SWAN_ALL_ROLES_MULTISELECT"] = "点击反应通过（进/出多选态均还原）"

log.info("=== 2. 角色编辑页（顶部）：选择按钮 点击反应 + 更多AI平台按钮 点击反应 ===")
assert aw.click_text("添加更多AI角色"), "进角色编辑页失败"
time.sleep(2.0)
assert on_text("自定义设置", 10), "未进入角色编辑页"
shot("04_role_editor_top")
assert verify_image("SWAN_ROLE_EDITOR_SELECT", SWAN_ROLE_EDITOR_SELECT), "选择按钮图未命中"
assert aw.click_image(SWAN_ROLE_EDITOR_SELECT, threshold=0.8, timeout=8), "点击选择按钮失败"
time.sleep(2.0)
shot("05_ai_images_via_select")
assert on_text("DIY形象", 8), "点击选择按钮后未进入 AI 形象页"
log.info("[通过] SWAN_ROLE_EDITOR_SELECT 点击 → AI 形象页")
RESULTS["SWAN_ROLE_EDITOR_SELECT"] = "点击反应通过（进 AI 形象页）"
assert verify_image("SWAN_ROLE_IMAGES_DIY_BTN", SWAN_ROLE_IMAGES_DIY_BTN), "DIY形象按钮图未命中"

log.info("=== 3. AI 形象页：DIY形象按钮 点击反应 → DIY 形象页 ===")
assert aw.click_image(SWAN_ROLE_IMAGES_DIY_BTN, threshold=0.8, timeout=8), "点击DIY形象按钮失败"
time.sleep(2.0)
shot("06_diy_via_btn")
assert on_text("0.2惠币", 8), "点击DIY形象按钮后未进入 DIY 形象页"
log.info("[通过] SWAN_ROLE_IMAGES_DIY_BTN 点击 → DIY 形象页")
RESULTS["SWAN_ROLE_IMAGES_DIY_BTN"] = "点击反应通过（进 DIY 形象页）"

log.info("=== 4. DIY 形象页：开始生成/上传照片卡（⛔ 只断言不点击）===")
assert verify_image("SWAN_DIY_GENERATE_BTN", SWAN_DIY_GENERATE_BTN), "开始生成按钮图未命中"
assert verify_image("SWAN_DIY_UPLOAD_CARD", SWAN_DIY_UPLOAD_CARD), "上传照片卡图未命中"

log.info("=== 5. 逐层返回：DIY → AI形象 → 角色编辑 ===")
aw.press_back()
time.sleep(1.5)
assert on_text("DIY形象", 8), "press_back 后未回 AI 形象页"
aw.press_back()
time.sleep(1.5)
assert on_text("自定义设置", 8), "press_back 后未回角色编辑页"

log.info("=== 6. 角色编辑页：更多AI平台按钮 点击反应 → AI 平台管理页 ===")
assert verify_image("SWAN_ROLE_EDITOR_MORE_PLATFORM", SWAN_ROLE_EDITOR_MORE_PLATFORM), "更多AI平台按钮图未命中"
assert aw.click_image(SWAN_ROLE_EDITOR_MORE_PLATFORM, threshold=0.8, timeout=8), "点击更多AI平台按钮失败"
time.sleep(2.0)
shot("07_ai_platform_via_btn")
assert on_text("平台", 8, region=TOPBAR_REGION), "点击更多AI平台按钮后未进入 AI 平台管理页"
log.info("[通过] SWAN_ROLE_EDITOR_MORE_PLATFORM 点击 → AI 平台管理页")
RESULTS["SWAN_ROLE_EDITOR_MORE_PLATFORM"] = "点击反应通过（进 AI 平台管理页）"

log.info("=== 7. AI 平台管理页：平台行按钮/顶栏标题（⛔ 行按钮不点击）===")
assert verify_image("SWAN_AI_PLATFORM_ROW_BTN", SWAN_AI_PLATFORM_ROW_BTN), "平台行按钮图未命中"
assert verify_image("SWAN_AI_PLATFORM_TITLE", SWAN_AI_PLATFORM_TITLE, region=TOPBAR_REGION), "顶栏平台标题图未命中"

log.info("=== 8. 角色编辑页（下半屏）：完成按钮（⛔ 只断言不点击）===")
aw.press_back()
time.sleep(1.5)
assert on_text("自定义设置", 8), "press_back 后未回角色编辑页"
for _ in range(3):
    aw.swipe_up()
    time.sleep(1.0)
shot("08_role_editor_bottom")
assert verify_image("SWAN_ROLE_EDITOR_DONE", SWAN_ROLE_EDITOR_DONE), "完成按钮图未命中"
for _ in range(4):
    aw.swipe_down()
    time.sleep(0.6)
shot("09_role_editor_back_top")

log.info("=== 9. AI 历史页：标题行（只断言存在）===")
back_to_home()
aw.click_text("AI", region=TOP_TAB_REGION)
time.sleep(1.5)
assert aw.click_text("历史对话记录"), "点历史对话记录标题行失败"
time.sleep(2.0)
shot("10_ai_history")
assert on_text("历史对话记录", 8, region=TOPBAR_REGION), "未进入 AI 历史页"
assert verify_image("SWAN_AI_HISTORY_TITLE", SWAN_AI_HISTORY_TITLE, region=TOPBAR_REGION), "AI历史标题行图未命中"
aw.press_back()
time.sleep(1.5)

log.info("=== 10. 收尾：复位首页·推荐 Tab ===")
assert aw.accessibility_exists("tab_recommend"), "不在首页（AI 历史页 press_back 应回 AI Tab）"
aw.click_accessibility("tab_recommend")
assert aw.wait_accessibility("tab_me", timeout=10), "未回到首页"
aw.click_text("推荐", region=TOP_TAB_REGION)
time.sleep(1.0)
shot("11_final_home_recommend")

log.info("=" * 60)
log.info("Wave 5 元素图真机验证结果汇总：")
for name, status in RESULTS.items():
    print(f"RESULT|{name}|{status}", flush=True)
failed = [n for n, s in RESULTS.items() if "失败" in s]
print("FINAL_STATE|首页·推荐 Tab（tab_me 可见）", flush=True)
if failed:
    print(f"FAILED_ITEMS|{failed}", flush=True)
    sys.exit(1)
print("ALL_PASSED", flush=True)
