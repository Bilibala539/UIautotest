"""
Explore long-press popup menu for two scenarios:
  1. Long-press the "测试测试" session row → OCR-dump everything that appears
  2. Long-press the "ChatGPT" top-row session-box → OCR-dump everything that appears

Goal: figure out the *real* menu item texts that mark_conversation_as_read /
close_conversation_box should match against (the current implementations look
for "设为已读" / "关闭", which are not being found).

Constraints (强约束):
  - Take over the already-running MuMu (port 16384) + already-logged-in popo
  - Never re-login, never force-stop popo
  - Never modify utils/ business code
  - Only screenshots + OCR full-text dump

Outputs:
  - explorer_output/screenshots/explore_longpress_20260521/*.png
  - Console: complete OCR text list for each screenshot
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

# Make project root importable when run as a script
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.aw import create_aw  # noqa: E402

SUBDIR = "explore_longpress_20260521"


def dump_ocr(aw, label: str) -> list:
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


def explore_one(aw, target_name: str, prefix: str) -> dict:
    """
    Explore long-press menu for a single conversation.

    Steps:
      1. focus window
      2. find target_name via OCR → get y
      3. screenshot the *before* state
      4. long_press(300, y, 1.5)
      5. sleep 1.5
      6. screenshot the *after* state (top of menu)
      7. swipe the menu up so the lower items become visible
      8. screenshot the *after-scroll* state
      9. dump full OCR for both states
     10. press_back ONCE to dismiss the menu (two backs would exit popo)
    """
    result = {
        "target": target_name,
        "found_pos": None,
        "before_screenshot": None,
        "after_screenshot": None,
        "after_scroll_screenshot": None,
        "menu_items": [],
        "menu_items_after_scroll": [],
    }

    print(f"\n############# Exploring long-press for: {target_name!r} #############")
    aw.driver.focus_window()
    time.sleep(0.5)

    before_path = aw.screenshot_for_explore(
        f"{prefix}_01_before_longpress.png", subdir=SUBDIR
    )
    result["before_screenshot"] = before_path
    print(f"[before-screenshot] {before_path}")

    pos = aw.find_text_by_ocr(target_name, timeout=10)
    if pos is None:
        print(f"[FAIL] Could not find {target_name!r} on screen — aborting this round")
        dump_ocr(aw, f"{target_name} (target NOT FOUND on screen)")
        return result

    target_y = pos[1]
    result["found_pos"] = (pos[0], pos[1])
    print(f"[ocr-found] {target_name!r} @ ({pos[0]}, {pos[1]}) — long-pressing (300, {target_y})")

    aw.long_press(300, target_y, duration=1.5)
    time.sleep(1.5)

    after_path = aw.screenshot_for_explore(
        f"{prefix}_02_after_longpress.png", subdir=SUBDIR
    )
    result["after_screenshot"] = after_path
    print(f"[after-screenshot] {after_path}")

    items = dump_ocr(aw, f"after long-press on {target_name!r} (initial menu)")
    result["menu_items"] = [
        {"text": it["text"], "cx": it["cx"], "cy": it["cy"], "bbox": list(it["bbox"])}
        for it in items
    ]

    # The popup menu is scrollable — swipe up from y=900 to y=400 (window
    # coords) to reveal the items below the fold (设为已读/关闭/etc.).
    print("[swipe-up] swiping menu up to reveal lower items ...")
    aw.swipe(270, 900, 270, 400, duration=0.6)
    time.sleep(1.2)

    after_scroll_path = aw.screenshot_for_explore(
        f"{prefix}_03_after_scroll.png", subdir=SUBDIR
    )
    result["after_scroll_screenshot"] = after_scroll_path
    print(f"[after-scroll-screenshot] {after_scroll_path}")

    items2 = dump_ocr(aw, f"after long-press on {target_name!r} (menu scrolled up)")
    result["menu_items_after_scroll"] = [
        {"text": it["text"], "cx": it["cx"], "cy": it["cy"], "bbox": list(it["bbox"])}
        for it in items2
    ]

    # Dismiss the menu so the next round starts clean — ONE back only, two
    # backs would exit popo to the MuMu launcher.
    print("[dismiss] press_back once to close the popup menu ...")
    aw.press_back()
    time.sleep(1.0)
    return result


def main():
    print("Connecting to running MuMu (instance_id=0, port 16384), no re-login ...")
    aw = create_aw(instance_id=0)

    # Bring popo window to the front; assumes popo is already running on the
    # message list page (caller's precondition).
    aw.driver.focus_window()
    time.sleep(0.6)

    # popo may be backgrounded behind MuMu's launcher even though it's still
    # logged in. Use `monkey` to bring it to foreground — this is the SAME
    # command MuMuBusiness.login() uses, but because popo is already logged in
    # the message-list page just resumes (no actual login flow).
    print("Bringing popo to foreground via monkey (no re-login) ...")
    aw._run_adb_command(
        "shell", "monkey", "-p", "com.netease.popo",
        "-c", "android.intent.category.LAUNCHER", "1",
    )
    time.sleep(4)
    aw.driver.focus_window()
    time.sleep(0.5)

    # Quick sanity check: take a screenshot + OCR dump of the resumed state so
    # we can confirm we're on the message list before any long-press.
    aw.screenshot_for_explore("00_initial_message_list.png", subdir=SUBDIR)
    dump_ocr(aw, "initial state (should be popo message list)")

    summary = {"rounds": []}

    # Round 1: long-press the "测试测试" session row (regular session list)
    summary["rounds"].append(explore_one(aw, "测试测试", "test_session"))

    # Brief pause + refocus so popo is back on the message list before round 2
    aw.driver.focus_window()
    time.sleep(0.5)

    # Round 2: long-press the "ChatGPT" top-row session-box (cy ~ 170)
    summary["rounds"].append(explore_one(aw, "ChatGPT", "chatgpt_box"))

    # Round 2b: ChatGPT tile may need a different x — its icon is on the LEFT
    # edge (cx≈39), not at x=300. Re-explore with x=icon_cx, y=icon_cy-40
    # (icon sits ABOVE the text label).
    aw.driver.focus_window()
    time.sleep(0.5)
    pos = aw.find_text_by_ocr("ChatGPT", timeout=10)
    if pos is not None:
        icon_x = pos[0]                # ≈ 39
        icon_y = max(pos[1] - 60, 80)  # ≈ 110 — the icon's center
        print(f"\n############# ROUND 2b: long-press ChatGPT TILE @ ({icon_x},{icon_y}) #############")
        before2 = aw.screenshot_for_explore("chatgpt_tile_01_before.png", subdir=SUBDIR)
        print(f"[before] {before2}")
        aw.long_press(icon_x, icon_y, duration=1.5)
        time.sleep(1.5)
        after2 = aw.screenshot_for_explore("chatgpt_tile_02_after.png", subdir=SUBDIR)
        print(f"[after] {after2}")
        items_b = dump_ocr(aw, "after long-press on ChatGPT TILE (icon coords)")
        # capture into summary for the JSON dump
        summary.setdefault("extra", []).append({
            "name": "chatgpt_tile",
            "icon_pos": [icon_x, icon_y],
            "before_screenshot": before2,
            "after_screenshot": after2,
            "menu_items": [
                {"text": it["text"], "cx": it["cx"], "cy": it["cy"]}
                for it in items_b
            ],
        })
        # Try a swipe in case the menu is partially below screen
        aw.swipe(270, 900, 270, 400, duration=0.6)
        time.sleep(1.0)
        after2s = aw.screenshot_for_explore("chatgpt_tile_03_after_scroll.png", subdir=SUBDIR)
        items_bs = dump_ocr(aw, "after long-press on ChatGPT TILE (scrolled)")
        summary["extra"][-1]["after_scroll_screenshot"] = after2s
        summary["extra"][-1]["menu_items_after_scroll"] = [
            {"text": it["text"], "cx": it["cx"], "cy": it["cy"]}
            for it in items_bs
        ]
        # Clean up
        aw.press_back()
        time.sleep(0.8)

    # Final guard: do NOT close popo. The per-round dismiss already presses
    # back once; nothing further needed. Just refocus and leave.
    aw.driver.focus_window()
    time.sleep(0.3)

    # Persist the menu-item dump to disk alongside the screenshots so the
    # report has a machine-readable record.
    out_dir = os.path.join(aw.EXPLORER_SCREENSHOT_DIR, SUBDIR)
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, "ocr_dump.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\n💾 OCR dump saved: {json_path}")
    print("\n✅ DONE — popo left running on message list (per spec).")


if __name__ == "__main__":
    main()
