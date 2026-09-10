# -*- coding: utf-8 -*-
"""Wave 4（平台/搜索域）元素图真机验证脚本（aw-verify，2026-09-10）。

验证 7 张暂存图（image_ai/flutter/）：
  SWAN_SEARCH_BACK / SWAN_SEARCH_SUBMIT / SWAN_SEARCH_CLEAR / SWAN_SEARCH_EMPTY
  SWAN_AUTH_GATE_LOGIN_BTN / SWAN_AUTH_GATE_ADD_BTN / SWAN_PLATFORM_RADIO_ROW_ARROW

⛔ 红线：SWAN_AUTH_GATE_LOGIN_BTN / SWAN_AUTH_GATE_ADD_BTN 只做存在性断言，绝不点击；
   门禁弹层只用 press_back 关闭；电台 Tab 的电台行不点击；禁止 tap 坐标。

用法：
    cd E:/UIAutotest
    set PLATFORM=flutter& set ANDROID_DEVICE_SERIAL=c0614b6a
    venv/Scripts/python.exe explorer_output/aw_element_tmp/wave4_verify.py
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
    SWAN_SEARCH_BACK,
    SWAN_SEARCH_SUBMIT,
    SWAN_SEARCH_CLEAR,
    SWAN_SEARCH_EMPTY,
    SWAN_AUTH_GATE_LOGIN_BTN,
    SWAN_AUTH_GATE_ADD_BTN,
    SWAN_PLATFORM_RADIO_ROW_ARROW,
)

# paddle/paddleocr 导入时已抢占 root logger，basicConfig 无效；
# 必须显式加 handler + 压掉 ppocr 的 DEBUG 噪声，否则 INFO 结果全部丢失。
logging.getLogger("ppocr").setLevel(logging.WARNING)
logging.getLogger("paddle").setLevel(logging.WARNING)
_root = logging.getLogger()
_root.setLevel(logging.INFO)
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
_root.addHandler(_handler)
log = logging.getLogger("wave4_verify")

SCREEN_W, SCREEN_H = 720, 1600
# 首页顶 Tab 行（y≈105-140，避开下方搜索条）
TOP_TAB_REGION = (0, 60, SCREEN_W, 90)          # y 60-150
# 搜索输入页顶栏（搜索按钮 y≈117-163，避开 T9 键盘区"搜索"键）
SEARCH_TOPBAR_REGION = (0, 100, SCREEN_W, 90)   # y 100-190
# 平台页左侧分类栏（窄条，避开右侧平台行文案）
PLATFORM_SIDEBAR_REGION = (0, 200, 100, 1250)   # x 0-100

RESULTS: dict[str, str] = {}


def verify_image(name: str, constant: str, region=None) -> bool:
    """存在性验证：0.8 阈值优先，失败降 0.7 重试（降阈值通过单独标记）。"""
    pos = aw.find_image(constant, threshold=0.8, timeout=8, region=region)
    if pos:
        RESULTS[name] = "通过(0.8)"
        log.info(f"[通过] {name} @ {pos}")
        return True
    log.warning(f"[重试] {name} 0.8 未命中，降阈值 0.7 重试")
    pos = aw.find_image(constant, threshold=0.7, timeout=5, region=region)
    if pos:
        RESULTS[name] = "降阈值通过(0.7)"
        log.info(f"[降阈值通过] {name} @ {pos}")
        return True
    RESULTS[name] = "失败"
    log.error(f"[失败] {name} 0.7 仍未命中")
    return False


def shot(step: str) -> None:
    """每步截图留证。"""
    aw.screenshot_for_explore(f"wave4_{step}.png", subdir="wave4_verify")
    time.sleep(0.3)


def gate_open(retries: int = 3) -> bool:
    """授权门禁弹层判据：语义树 desc='纱罩'（dump 瞬时失败自动重试）。"""
    for _ in range(retries):
        nodes = aw.dump_semantics()
        if len(nodes) > 2:
            return any((n.get("content_desc") or "") == "纱罩" for n in nodes)
        time.sleep(1.0)
    return False


def assert_gate_closed(context: str) -> None:
    assert not gate_open(), f"{context}: press_back 后纱罩仍存在，门禁未关闭"


def back_to_home(presses: int = 3) -> None:
    """press_back 逐步返回，直到看到 tab_me（每次按下前先检查，避免在首页误退 App）。"""
    for _ in range(presses):
        if aw.accessibility_exists("tab_me"):
            return
        aw.press_back()
        time.sleep(1.5)
    assert aw.accessibility_exists("tab_me"), "未能回到首页（tab_me 不可见）"


def enter_top_tab(label: str) -> None:
    """回首页 → 点顶部 Tab（顶 Tab 选择持久化，须显式点）。"""
    aw.click_accessibility("tab_recommend")
    assert aw.wait_accessibility("tab_me", timeout=10), "未回到首页"
    aw.click_text(label, region=TOP_TAB_REGION)
    time.sleep(1.2)


# =====================================================================
driver = FlutterAndroidDriver(serial="c0614b6a")
user = SwanUser(driver=driver)
aw = user.aw
PKG = "com.swan.network"

log.info("=== 0. 冷启动 App，确认登录态 ===")
driver.stop_app(PKG)
time.sleep(1.5)
driver.start_app(PKG)
assert aw.wait_accessibility("tab_me", timeout=25), (
    "App 启动后未进入首页（tab_me 不可见），可能处于登录页，需人工确认登录态"
)
log.info("已在首页（已登录）")
shot("00_home_start")

# ---------------------------------------------------------------------
log.info("=== 1. 搜索域：首页·音乐 Tab → 搜索输入页 ===")
enter_top_tab("音乐")
aw.swipe_down(distance=400)
aw.swipe_down(distance=400)  # 滚动位复位
time.sleep(0.8)
shot("01_music_tab")
aw.click_text("跨平台搜索音乐")
time.sleep(1.5)
assert aw.text_exists("搜索歌曲或艺术家等", timeout=8), "未进入搜索输入页（hint 不可见）"
shot("02_search_input_page")

verify_image("SWAN_SEARCH_BACK", SWAN_SEARCH_BACK)
verify_image("SWAN_SEARCH_SUBMIT", SWAN_SEARCH_SUBMIT, region=SEARCH_TOPBAR_REGION)

log.info("=== 2. 输入 abc → X 清空按钮出现 → 顶栏提交搜索 ===")
aw.click_text("搜索歌曲或艺术家等", timeout=8)
aw.input_text("abc")
time.sleep(1.2)
shot("03_search_typed_abc")
verify_image("SWAN_SEARCH_CLEAR", SWAN_SEARCH_CLEAR)

# ⚠️ region 限定顶栏，避开 T9 键盘区同名"搜索"键
aw.click_image(SWAN_SEARCH_SUBMIT, threshold=0.8, timeout=8,
               region=SEARCH_TOPBAR_REGION)
time.sleep(2.5)
shot("04_search_results_abc")
verify_image("SWAN_SEARCH_EMPTY", SWAN_SEARCH_EMPTY)

log.info("=== 3. 结果页点返回箭头回输入页（关键词不回填、X 消失为已知行为）===")
aw.click_image(SWAN_SEARCH_BACK, threshold=0.8, timeout=8)
time.sleep(1.5)
shot("05_back_to_input_page")
assert aw.text_exists("搜索歌曲或艺术家等", timeout=8), "返回后未回到搜索输入页"

log.info("=== 4. 离开搜索域回首页 ===")
back_to_home()
shot("06_back_home")

# ---------------------------------------------------------------------
log.info("=== 5. 授权门禁变体 A（添加按钮）：首页·电台 Tab → 全国电台分组标题 ===")
enter_top_tab("电台")
aw.swipe_down(distance=400)
aw.swipe_down(distance=400)
time.sleep(0.8)
shot("07_radio_tab")
aw.click_text("全国电台")  # 分组标题（整行可点），进多级页才触发门禁
time.sleep(1.8)
shot("08_auth_gate_add")
assert gate_open(), "变体 A：纱罩未出现，门禁弹层未弹出"
verify_image("SWAN_AUTH_GATE_ADD_BTN", SWAN_AUTH_GATE_ADD_BTN)  # ⛔ 只断言不点击
aw.press_back()
time.sleep(1.2)
assert_gate_closed("变体 A")
shot("09_auth_gate_add_closed")

# ---------------------------------------------------------------------
log.info("=== 6. 授权门禁变体 B（授权登录按钮）：首页·音乐 Tab → QQ音乐区块标题 ===")
enter_top_tab("音乐")
aw.swipe_down(distance=400)
aw.swipe_down(distance=400)
time.sleep(0.8)
shot("10_music_tab_for_gate")
aw.click_text("QQ音乐")  # 平台区块标题
time.sleep(1.8)
shot("11_auth_gate_login")
assert gate_open(), "变体 B：纱罩未出现，门禁弹层未弹出"
verify_image("SWAN_AUTH_GATE_LOGIN_BTN", SWAN_AUTH_GATE_LOGIN_BTN)  # ⛔ 只断言不点击
aw.press_back()
time.sleep(1.2)
assert_gate_closed("变体 B")
shot("12_auth_gate_login_closed")

# ---------------------------------------------------------------------
log.info("=== 7. 平台页：电台分类 → 电台行箭头 ===")
aw.click_accessibility("tab_platform")
assert aw.wait_accessibility("platform_page", timeout=10), "未进入平台页"
time.sleep(1.0)
shot("13_platform_page")
# 左侧分类持久：显式切到"电台"（region 限定左侧栏，避开右侧行文案"全国电台"）
aw.click_text("电台", region=PLATFORM_SIDEBAR_REGION)
time.sleep(1.2)
shot("14_platform_radio_category")
verify_image("SWAN_PLATFORM_RADIO_ROW_ARROW", SWAN_PLATFORM_RADIO_ROW_ARROW)

log.info("=== 8. 可选链路：点电台行箭头 → 门禁弹出 → press_back 关闭 ===")
aw.click_image(SWAN_PLATFORM_RADIO_ROW_ARROW, threshold=0.8, timeout=8)
time.sleep(1.8)
shot("15_platform_arrow_gate")
assert gate_open(), "平台页箭头点击后纱罩未出现"
aw.press_back()
time.sleep(1.2)
assert_gate_closed("平台页箭头")
shot("16_platform_arrow_gate_closed")

# ---------------------------------------------------------------------
log.info("=== 9. 收尾：复位到首页·推荐 Tab ===")
aw.click_accessibility("tab_recommend")
assert aw.wait_accessibility("tab_me", timeout=10), "未回到首页"
aw.click_text("推荐", region=TOP_TAB_REGION)  # 顶 Tab 复位到推荐
time.sleep(1.0)
shot("17_final_home_recommend")

log.info("=" * 60)
log.info("Wave 4 元素图验证结果汇总：")
for name, status in RESULTS.items():
    print(f"RESULT|{name}|{status}", flush=True)
failed = [n for n, s in RESULTS.items() if s == "失败"]
print("FINAL_STATE|首页·推荐 Tab（tab_me 可见）", flush=True)
if failed:
    print(f"FAILED_ITEMS|{failed}", flush=True)
    sys.exit(1)
print("ALL_PASSED", flush=True)
