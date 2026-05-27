"""
Explore the "会话盒子" feature on POPO Android.

Goal: figure out what 会话盒子 actually IS on the message-list page so that
row6 (盒子-设为已读) / row7 (盒子-关闭) / row9 (会话盒子和服务号助手的灰点
消失-设为已读) can be implemented correctly.

Hypotheses to confirm/reject:
  H1. 会话盒子 is a SESSION ROW in the main conversation list (e.g. titled
      "会话盒子" / "我的盒子" / "工作盒子"). Long-press on that row → menu
      contains "设为已读" / "关闭".
  H2. 会话盒子 is the TOP horizontal scrolling tile-strip (ChatGPT, 网易
      内购福, etc.) — a previous explorer already proved this strip does NOT
      respond to long-press.
  H3. There is a separate sidebar / settings entry for "会话盒子管理".

What we already know from explore_longpress_20260521/ocr_dump.json:
  - Long-pressing "测试测试" gives a popup-menu whose items (after scroll-up)
    include 置顶 / 设为未读 / 添加到待处理 / 添加至分组 / 关闭消息提醒 /
    "添加到会话盒子" / 关闭会话.
  - "添加到会话盒子" suggests 会话盒子 is a per-conversation flag that, once
    set, makes the conversation appear inside a special container. We need to
    find that container.

This script (constraints: no re-login, no force-stop, no business code edits):
  1. Take over running MuMu instance 0 (port 16384) + already-logged-in popo.
  2. Bring popo to foreground via monkey (same as explore_longpress_menu.py).
  3. Snapshot+OCR initial message list state.
  4. Swipe the conversation list DOWN repeatedly (toward the top) and OCR-dump
     every screen, collecting all unique visible text — looking for any
     "盒子" string.
  5. Then swipe UP repeatedly (toward the bottom) and same.
  6. Long-press a normal session row ("测试测试") and OCR-dump the FULL menu,
     this time scrolling the menu both up AND down to make sure we catch every
     menu item. Look for any "盒子" / "关闭" entry beyond the previously-seen
     "添加到会话盒子" / "关闭会话".
  7. Open the sidebar (top-left avatar) and OCR-dump it — look for a "会话盒子
     管理" / "我的盒子" entry.
  8. press_back to message list, leave popo running.

Outputs:
  - explorer_output/screenshots/explore_conversation_box_20260521/*.png
  - explorer_output/screenshots/explore_conversation_box_20260521/ocr_dump.json
"""

import os
import sys
import time
import json
import io

# Force stdout/stderr to UTF-8 so Chinese + emojis don't blow up under PowerShell GBK
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

# Make project root importable
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.aw import create_aw  # noqa: E402

SUBDIR = "explore_conversation_box_20260521"


def dump_ocr(aw, label):
    """Run a full-page OCR scan and pretty-print every recognized line."""
    print(f"\n========== OCR DUMP: {label} ==========")
    items = aw.ocr_scan_page()
    if not items:
        print("  (no text recognized)")
        return []
    for i, it in enumerate(items):
        print(
            f"  [{i:02d}] '{it['text']}' "
            f"@ ({it['cx']},{it['cy']}) "
            f"bbox={it['bbox']} "
            f"conf={it.get('confidence', 0):.3f}"
        )
    print(f"  ---- {len(items)} items ----")
    return items


def items_to_records(items):
    return [
        {"text": it["text"], "cx": it["cx"], "cy": it["cy"], "bbox": list(it["bbox"])}
        for it in items
    ]


def check_for_box_keywords(items, label):
    """Print any items whose text contains '盒子' or '关闭'."""
    print(f"\n>>> Keyword scan ({label}): looking for '盒子' / '关闭'")
    hits = []
    for it in items:
        t = it["text"]
        if "盒子" in t or "关闭" in t:
            print(f"    HIT: '{t}' @ ({it['cx']},{it['cy']})")
            hits.append({"text": t, "cx": it["cx"], "cy": it["cy"]})
    if not hits:
        print("    (no hits)")
    return hits


def main():
    print("Connecting to running MuMu (instance_id=0, port 16384), no re-login ...")
    aw = create_aw(instance_id=0)

    aw.driver.focus_window()
    time.sleep(0.6)

    # popo may be backgrounded — bring to foreground via monkey (same as
    # MuMuBusiness.login() does, but popo is already logged in so it's a resume)
    print("Bringing popo to foreground via monkey (no re-login) ...")
    aw._run_adb_command(
        "shell", "monkey", "-p", "com.netease.popo",
        "-c", "android.intent.category.LAUNCHER", "1",
    )
    time.sleep(4)
    aw.driver.focus_window()
    time.sleep(0.5)

    summary = {"phases": []}

    # ---- Phase 0: initial state ----
    print("\n############ Phase 0: initial message-list snapshot ############")
    aw.screenshot_for_explore("00_initial.png", subdir=SUBDIR)
    items0 = dump_ocr(aw, "phase 0 — initial message list")
    hits0 = check_for_box_keywords(items0, "phase 0")
    summary["phases"].append({
        "name": "phase0_initial",
        "items": items_to_records(items0),
        "box_hits": hits0,
    })

    # ---- Phase 1: swipe DOWN repeatedly (scroll list toward TOP) ----
    # First force the list to its top — repeated swipe down on the list area
    # below the top tile strip. Avoid the top tile strip (cy~170-220).
    print("\n############ Phase 1: scroll conversation list toward TOP ############")
    for i in range(3):
        # swipe-down means start lower → end higher, which on Android scrolls list UP
        # (i.e. shows earlier rows). We want to make sure we're at the TOP of the
        # message list before starting downward scan.
        aw.swipe(270, 350, 270, 700, duration=0.5)
        time.sleep(0.6)
    aw.screenshot_for_explore("01_top_of_list.png", subdir=SUBDIR)
    items_top = dump_ocr(aw, "phase 1 — at top of conversation list")
    hits_top = check_for_box_keywords(items_top, "phase 1")
    summary["phases"].append({
        "name": "phase1_top",
        "items": items_to_records(items_top),
        "box_hits": hits_top,
    })

    # ---- Phase 2: swipe UP repeatedly (scroll list DOWN, see later rows) ----
    print("\n############ Phase 2: scroll conversation list DOWNWARD (reveal later rows) ############")
    seen_texts = set(it["text"] for it in items_top)
    all_unique = list(items_to_records(items_top))
    box_hits_all = list(hits_top)
    for step in range(8):
        # avoid the top tile strip — start swipe at y=800, end at y=300
        aw.swipe(270, 800, 270, 300, duration=0.5)
        time.sleep(0.8)
        png = aw.screenshot_for_explore(f"02_scroll_down_{step:02d}.png", subdir=SUBDIR)
        items_step = dump_ocr(aw, f"phase 2 — step {step}")
        hits_step = check_for_box_keywords(items_step, f"phase 2 step {step}")
        # collect unique
        for it in items_step:
            if it["text"] not in seen_texts:
                seen_texts.add(it["text"])
                all_unique.append({
                    "text": it["text"],
                    "cx": it["cx"], "cy": it["cy"],
                    "bbox": list(it["bbox"]),
                    "first_seen_step": step,
                })
        box_hits_all.extend(hits_step)
    summary["phases"].append({
        "name": "phase2_scroll_down",
        "all_unique_visible_text_during_scroll": all_unique,
        "box_hits": box_hits_all,
    })

    # ---- Phase 3: scroll back to top of list ----
    print("\n############ Phase 3: scroll back to TOP ############")
    for _ in range(10):
        aw.swipe(270, 350, 270, 800, duration=0.4)
        time.sleep(0.4)
    aw.screenshot_for_explore("03_back_to_top.png", subdir=SUBDIR)

    # ---- Phase 4: long-press "测试测试" and FULLY scroll the menu ----
    # We already know the menu contains 添加到会话盒子 + 关闭会话. This time
    # try scrolling the menu DOWN as well as UP, in case there's an item below
    # 关闭会话 that we missed.
    print("\n############ Phase 4: long-press '测试测试', scroll menu both directions ############")
    pos = aw.find_text_by_ocr("测试测试", timeout=10)
    if pos is None:
        print("  [WARN] could not find '测试测试' on screen")
        summary["phases"].append({
            "name": "phase4_longpress_menu",
            "error": "测试测试 not found",
        })
    else:
        target_y = pos[1]
        print(f"  long-pressing (300, {target_y}) ...")
        aw.long_press(300, target_y, duration=1.5)
        time.sleep(1.5)
        aw.screenshot_for_explore("04_menu_initial.png", subdir=SUBDIR)
        items_m0 = dump_ocr(aw, "phase 4 — menu initial (no scroll)")
        hits_m0 = check_for_box_keywords(items_m0, "menu initial")

        # Scroll menu UP once (start_y high, end_y low) to reveal items below
        aw.swipe(270, 900, 270, 400, duration=0.6)
        time.sleep(1.2)
        aw.screenshot_for_explore("05_menu_scroll_up_1.png", subdir=SUBDIR)
        items_m1 = dump_ocr(aw, "phase 4 — menu scrolled UP once")
        hits_m1 = check_for_box_keywords(items_m1, "menu scroll up 1")

        # Scroll menu UP again — confirm we hit the bottom
        aw.swipe(270, 900, 270, 400, duration=0.6)
        time.sleep(1.0)
        aw.screenshot_for_explore("06_menu_scroll_up_2.png", subdir=SUBDIR)
        items_m2 = dump_ocr(aw, "phase 4 — menu scrolled UP twice")
        hits_m2 = check_for_box_keywords(items_m2, "menu scroll up 2")

        # Scroll menu DOWN to recover the top items
        aw.swipe(270, 300, 270, 800, duration=0.6)
        time.sleep(1.0)
        aw.screenshot_for_explore("07_menu_scroll_down.png", subdir=SUBDIR)
        items_m3 = dump_ocr(aw, "phase 4 — menu scrolled DOWN")
        hits_m3 = check_for_box_keywords(items_m3, "menu scroll down")

        summary["phases"].append({
            "name": "phase4_longpress_menu",
            "target": "测试测试",
            "found_pos": list(pos),
            "menu_initial": items_to_records(items_m0),
            "menu_scroll_up_1": items_to_records(items_m1),
            "menu_scroll_up_2": items_to_records(items_m2),
            "menu_scroll_down": items_to_records(items_m3),
            "all_box_hits": hits_m0 + hits_m1 + hits_m2 + hits_m3,
        })

        # Dismiss menu
        aw.press_back()
        time.sleep(1.0)

    # ---- Phase 5: open sidebar (top-left avatar) ----
    print("\n############ Phase 5: open sidebar, look for box-management entry ############")
    # Sidebar opens by tapping top-left avatar (around x=30, y=80 on 540x960
    # message-list page). But to avoid hard-coding we go through the existing
    # PPUser/business helper if available — fall back to swipe-from-left.
    try:
        # swipe from left edge into screen — opens sidebar
        aw.swipe(5, 480, 400, 480, duration=0.5)
        time.sleep(1.5)
        aw.screenshot_for_explore("08_sidebar.png", subdir=SUBDIR)
        items_sb = dump_ocr(aw, "phase 5 — sidebar")
        hits_sb = check_for_box_keywords(items_sb, "sidebar")

        # Try scrolling the sidebar to see if there's a 会话盒子 entry below the fold
        aw.swipe(270, 800, 270, 300, duration=0.5)
        time.sleep(1.0)
        aw.screenshot_for_explore("09_sidebar_scrolled.png", subdir=SUBDIR)
        items_sb2 = dump_ocr(aw, "phase 5 — sidebar scrolled")
        hits_sb2 = check_for_box_keywords(items_sb2, "sidebar scrolled")

        summary["phases"].append({
            "name": "phase5_sidebar",
            "sidebar_items": items_to_records(items_sb),
            "sidebar_scrolled_items": items_to_records(items_sb2),
            "box_hits": hits_sb + hits_sb2,
        })

        # Close sidebar (tap right edge or press back)
        aw.press_back()
        time.sleep(1.0)
    except Exception as e:
        print(f"  [WARN] sidebar phase failed: {e}")
        summary["phases"].append({
            "name": "phase5_sidebar",
            "error": str(e),
        })

    # ---- Final: ensure we're back on message list ----
    print("\n############ Cleanup: ensure popo is on message list ############")
    aw.driver.focus_window()
    time.sleep(0.5)
    final_path = aw.screenshot_for_explore("99_final_state.png", subdir=SUBDIR)
    print(f"  final screenshot: {final_path}")
    final_items = dump_ocr(aw, "final state")

    # Persist
    out_dir = os.path.join(aw.EXPLORER_SCREENSHOT_DIR, SUBDIR)
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, "ocr_dump.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\nOCR dump saved: {json_path}")
    print("DONE — popo left running on message list (per spec).")


if __name__ == "__main__":
    main()
