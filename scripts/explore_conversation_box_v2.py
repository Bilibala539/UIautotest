"""
Phase-2 exploration: now that we know what hidden state Phase-1 of v1 stumbled
into ("最近" application launcher page from accidentally tap-clicking the
"最近" tab while initiating swipe), redo the message-list scan with safer
swipe geometry.

Phase 1 of v1 swiped from (270, 350) — but cy=271 is the "最近" TAB and
cy=337 is the first conversation row, so the press-down on (270, 350) coupled
with a slow swipe (0.5s) registered as a TAP on "最近", which navigated to
the launcher page. From there nothing was scrollable.

This v2 script:
  - Fresh start: ensure popo is on message list (press_back if needed)
  - Use swipes that start CLEARLY below the tabs (cy >= 450) and end at
    cy >= 200 so neither endpoint hits a tappable element
  - After confirming the message list, do these phases:

    A. Initial OCR snapshot at message list
    B. Try TAPPING each of the four tabs (最近 / @我 / 未读 / 待处理) and
       OCR-dump each — even though "会话盒子" isn't visible as a tab, maybe
       one of these tabs has "会话盒子" entries above the conversation rows.
    C. Long-press "测试测试" and EXHAUSTIVELY scroll the menu to capture
       every item (including any "从盒子移除" / "关闭盒子" below 关闭会话).
    D. Long-press "ChatGPT服务号" specifically — the case row9 talks about
       "服务号助手", which is exactly this row, and its menu may differ from
       a normal user's menu.
    E. From the LIST, swipe upward several times on a safe x to confirm
       there's no hidden "会话盒子" row beyond the visible 5-6 conversations.
    F. Try clicking the top-left avatar to open the real sidebar and scan it.
"""

import os
import sys
import time
import json
import io

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.aw import create_aw  # noqa: E402

SUBDIR = "explore_conversation_box_20260521"


def dump_ocr(aw, label):
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


def keyword_hits(items, label):
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


def ensure_message_list(aw):
    """Press back until we see "消息" + bottom tab bar (a hint we're at message list)."""
    for attempt in range(4):
        items = aw.ocr_scan_page()
        texts = {it["text"] for it in items}
        # heuristic: message list has both top "消息" header + bottom "消息" tab + tab row "最近 / 未读"
        if "消息" in texts and "最近" in texts and ("@我2" in texts or any("@我" in t for t in texts)):
            print(f"  [ensure_message_list] confirmed (attempt {attempt})")
            return True
        print(f"  [ensure_message_list] not on msg list — pressing back ({attempt})")
        aw.press_back()
        time.sleep(1.0)
    return False


def safe_swipe_up(aw, distance=400):
    """
    Swipe up using coords that don't accidentally tap a tab/tile.
    Start at cy=850 (in conversation list area), end at cy=300.
    Avoid cy=170-220 (top tiles) and cy=271 (tabs).
    """
    aw.swipe(270, 850, 270, 850 - distance, duration=0.6)


def safe_swipe_down(aw, distance=400):
    aw.swipe(270, 450, 270, 450 + distance, duration=0.6)


def main():
    print("Connecting to running MuMu (instance_id=0, port 16384), no re-login ...")
    aw = create_aw(instance_id=0)

    aw.driver.focus_window()
    time.sleep(0.6)

    print("Bringing popo to foreground via monkey (no re-login) ...")
    aw._run_adb_command(
        "shell", "monkey", "-p", "com.netease.popo",
        "-c", "android.intent.category.LAUNCHER", "1",
    )
    time.sleep(4)
    aw.driver.focus_window()
    time.sleep(0.5)

    summary = {"phases": []}

    # ---- Phase A: initial state — ensure on message list ----
    print("\n############ Phase A: confirm message list, snapshot ############")
    aw.screenshot_for_explore("v2_A0_after_resume.png", subdir=SUBDIR)
    if not ensure_message_list(aw):
        print("  [WARN] could not confirm message list — proceeding anyway")
    aw.screenshot_for_explore("v2_A1_message_list.png", subdir=SUBDIR)
    items_a = dump_ocr(aw, "v2 phase A — message list")
    hits_a = keyword_hits(items_a, "phase A")
    summary["phases"].append({
        "name": "phaseA_message_list",
        "items": items_to_records(items_a),
        "box_hits": hits_a,
    })

    # ---- Phase B: tap each tab (最近 / @我 / 未读 / 待处理) ----
    # Also try tapping a hypothetical "会话盒子" tab if OCR shows one (it didn't,
    # but be defensive).
    print("\n############ Phase B: visit each tab ############")
    tab_names = ["最近", "@我2", "未读99+", "待处理1"]
    for tab in tab_names:
        print(f"\n  >>> Tab: {tab}")
        pos = aw.find_text_by_ocr(tab, timeout=5)
        if pos is None:
            # try without trailing badge
            short = tab.split("@")[-1] if "@" in tab else tab.rstrip("0123456789+")
            pos = aw.find_text_by_ocr(short, timeout=3)
        if pos is None:
            print(f"    [skip] tab '{tab}' not found")
            summary["phases"].append({"name": f"phaseB_tab_{tab}", "skipped": True})
            continue
        aw.tap(pos[0], pos[1])
        time.sleep(1.2)
        png = aw.screenshot_for_explore(f"v2_B_tab_{tab}.png", subdir=SUBDIR)
        items_t = dump_ocr(aw, f"phase B — tab {tab}")
        hits_t = keyword_hits(items_t, f"tab {tab}")
        summary["phases"].append({
            "name": f"phaseB_tab_{tab}",
            "items": items_to_records(items_t),
            "box_hits": hits_t,
        })

    # Always come back to "最近" (the default) after tab tour
    pos = aw.find_text_by_ocr("最近", timeout=5)
    if pos is not None:
        aw.tap(pos[0], pos[1])
        time.sleep(1.0)

    # ---- Phase C: long-press 测试测试, dump menu exhaustively ----
    print("\n############ Phase C: long-press '测试测试' menu, exhaustive scan ############")
    pos = aw.find_text_by_ocr("测试测试", timeout=10)
    if pos is None:
        print("  [WARN] 测试测试 not found — skipping phase C")
        summary["phases"].append({"name": "phaseC_longpress", "error": "测试测试 not found"})
    else:
        target_y = pos[1]
        aw.long_press(300, target_y, duration=1.5)
        time.sleep(1.5)
        aw.screenshot_for_explore("v2_C0_menu_initial.png", subdir=SUBDIR)
        m0 = dump_ocr(aw, "C — menu initial")
        h0 = keyword_hits(m0, "menu initial")

        # exhaustive menu scrolling
        all_menu_dumps = [items_to_records(m0)]
        all_box_hits = list(h0)

        # Scroll up multiple times to reveal items below the visible portion
        for k in range(3):
            aw.swipe(270, 850, 270, 350, duration=0.6)
            time.sleep(1.0)
            png = aw.screenshot_for_explore(f"v2_C1_scroll_up_{k}.png", subdir=SUBDIR)
            mk = dump_ocr(aw, f"C — menu scroll up #{k+1}")
            hk = keyword_hits(mk, f"menu scroll up #{k+1}")
            all_menu_dumps.append(items_to_records(mk))
            all_box_hits.extend(hk)

        # Try scroll down too (in case there were items above the initial view)
        for k in range(3):
            aw.swipe(270, 200, 270, 800, duration=0.6)
            time.sleep(1.0)
            png = aw.screenshot_for_explore(f"v2_C2_scroll_down_{k}.png", subdir=SUBDIR)
            mk = dump_ocr(aw, f"C — menu scroll down #{k+1}")
            hk = keyword_hits(mk, f"menu scroll down #{k+1}")
            all_menu_dumps.append(items_to_records(mk))
            all_box_hits.extend(hk)

        summary["phases"].append({
            "name": "phaseC_longpress_test_session",
            "target": "测试测试",
            "found_pos": list(pos),
            "menu_dumps": all_menu_dumps,
            "all_box_hits": all_box_hits,
        })

        aw.press_back()
        time.sleep(1.0)

    # ---- Phase D: long-press ChatGPT服务号 (the actual service-account row) ----
    print("\n############ Phase D: long-press ChatGPT服务号 row ############")
    pos = aw.find_text_by_ocr("ChatGPT服务号", timeout=8)
    if pos is None:
        # fallback to "ChatGPT" but only if cy > 250 (avoid the tile strip at cy~205)
        items = aw.ocr_scan_page()
        cands = [it for it in items if "ChatGPT" in it["text"] and it["cy"] > 250]
        pos = (cands[0]["cx"], cands[0]["cy"]) if cands else None
    if pos is None:
        print("  [WARN] ChatGPT服务号 row not found — skipping D")
        summary["phases"].append({"name": "phaseD_longpress_service", "error": "service row not found"})
    else:
        print(f"  long-pressing service row @ ({pos[0]}, {pos[1]})")
        aw.long_press(300, pos[1], duration=1.5)
        time.sleep(1.5)
        aw.screenshot_for_explore("v2_D0_service_menu.png", subdir=SUBDIR)
        d0 = dump_ocr(aw, "D — service menu initial")
        hd0 = keyword_hits(d0, "service menu initial")

        all_d_dumps = [items_to_records(d0)]
        all_d_hits = list(hd0)
        for k in range(3):
            aw.swipe(270, 850, 270, 350, duration=0.6)
            time.sleep(1.0)
            aw.screenshot_for_explore(f"v2_D1_service_scroll_up_{k}.png", subdir=SUBDIR)
            dk = dump_ocr(aw, f"D — service menu scroll up #{k+1}")
            hk = keyword_hits(dk, f"service menu scroll up #{k+1}")
            all_d_dumps.append(items_to_records(dk))
            all_d_hits.extend(hk)

        summary["phases"].append({
            "name": "phaseD_longpress_service",
            "found_pos": list(pos),
            "menu_dumps": all_d_dumps,
            "all_box_hits": all_d_hits,
        })

        aw.press_back()
        time.sleep(1.0)

    # ---- Phase E: scroll the conversation list to see if there are more rows ----
    print("\n############ Phase E: scroll conversation list to find any '盒子' row ############")
    seen_texts = set()
    all_unique = []
    for step in range(8):
        safe_swipe_up(aw, distance=500)
        time.sleep(0.8)
        png = aw.screenshot_for_explore(f"v2_E_scroll_list_{step:02d}.png", subdir=SUBDIR)
        items_e = dump_ocr(aw, f"E — list scroll step {step}")
        hits_e = keyword_hits(items_e, f"list step {step}")
        for it in items_e:
            if it["text"] not in seen_texts:
                seen_texts.add(it["text"])
                all_unique.append({
                    "text": it["text"],
                    "cx": it["cx"], "cy": it["cy"],
                    "first_seen_step": step,
                })
    summary["phases"].append({
        "name": "phaseE_scroll_list",
        "all_unique_text_during_scroll": all_unique,
    })

    # Scroll back to top
    for _ in range(8):
        safe_swipe_down(aw, distance=500)
        time.sleep(0.5)

    # ---- Phase F: open real sidebar by tapping the top-left avatar ----
    print("\n############ Phase F: tap top-left avatar to open sidebar ############")
    # Avatar is at cx≈30, cy≈70 (just left of the "消息" header)
    aw.tap(30, 70)
    time.sleep(1.5)
    aw.screenshot_for_explore("v2_F0_sidebar_opened.png", subdir=SUBDIR)
    items_f = dump_ocr(aw, "F — sidebar (after avatar tap)")
    hits_f = keyword_hits(items_f, "sidebar")
    summary["phases"].append({
        "name": "phaseF_sidebar",
        "items": items_to_records(items_f),
        "box_hits": hits_f,
    })

    # Scroll sidebar in case it's longer
    aw.swipe(150, 800, 150, 300, duration=0.6)
    time.sleep(1.0)
    aw.screenshot_for_explore("v2_F1_sidebar_scrolled.png", subdir=SUBDIR)
    items_f2 = dump_ocr(aw, "F — sidebar scrolled")
    hits_f2 = keyword_hits(items_f2, "sidebar scrolled")
    summary["phases"].append({
        "name": "phaseF_sidebar_scrolled",
        "items": items_to_records(items_f2),
        "box_hits": hits_f2,
    })

    # Close sidebar
    aw.press_back()
    time.sleep(1.0)

    # Final
    aw.driver.focus_window()
    time.sleep(0.3)
    aw.screenshot_for_explore("v2_99_final.png", subdir=SUBDIR)

    out_dir = os.path.join(aw.EXPLORER_SCREENSHOT_DIR, SUBDIR)
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, "v2_ocr_dump.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\nv2 OCR dump saved: {json_path}")
    print("DONE.")


if __name__ == "__main__":
    main()
