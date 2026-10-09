# -*- coding: utf-8 -*-
"""POC step1: OCR all candidate full-screen screenshots from main workspace (read-only).
Output: poc_aw/ocr_texts.json  {relpath: {"text": ..., "n_lines": ..., "size": [w,h]}}
"""
import json, pathlib, sys

SRC = pathlib.Path("E:/UIAutotest/explorer_output")
OUT = pathlib.Path(__file__).parent / "ocr_texts.json"

CANDIDATES = [
    # verify_run3 (tab switching / device switch regression)
    "verify_run3/tab_AI.png", "verify_run3/tab_音乐.png", "verify_run3/tab_电台.png",
    "verify_run3/tab_推荐.png", "verify_run3/tab_可视音箱.png",
    "verify_run3/FAIL_top_AI.png", "verify_run3/FAIL_top_音乐.png", "verify_run3/FAIL_top_电台.png",
    "verify_run3/FAIL_top_推荐.png", "verify_run3/FAIL_top_可视音箱.png",
    "verify_run3/page_device.png", "verify_run3/page_me.png", "verify_run3/page_platform.png",
    "verify_run3/fix_AI_ADD_ROLE.png", "verify_run3/fix_HOME_SEARCH_BAR.png",
    "verify_run3/fix_RADIO_SEARCH_BAR.png", "verify_run3/fix_VISION_HINT.png",
    "verify_run3/state_before_back.png", "verify_run3/state_after_back.png",
    "verify_run3/diag_after_goto_home.png", "verify_run3/after_relaunch_full.png",
    "verify_run3/after_select_card.png", "verify_run3/FAIL_select_card.png",
    "verify_run3/diag_before_sel_assert.png", "verify_run3/diag_before_sel_assert_music.png",
    "verify_run3/search_retrigger_state.png",
    # verify_run2 / verify_regression1
    "verify_run2/final_home.png",
    "verify_regression1/final_home.png", "verify_regression1/after_pytest1.png",
    "verify_regression1/probe1.png", "verify_regression1/probe_top.png",
    "verify_regression1/state_device.png", "verify_regression1/state_home.png",
    "verify_regression1/state_home2.png", "verify_regression1/state_me.png",
    "verify_regression1/state_platform.png", "verify_regression1/state_player.png",
    "verify_regression1/state_restored.png", "verify_regression1/state_sheet.png",
    "verify_regression1/state_volume_popup.png", "verify_regression1/volume_minus5.png",
    # domain3
    "aw_element_tmp/domain3/home.png", "aw_element_tmp/domain3/device_page.png",
    "aw_element_tmp/domain3/device_selected.png", "aw_element_tmp/domain3/platform_page.png",
    "aw_element_tmp/domain3/player_full.png", "aw_element_tmp/domain3/playlist_detail.png",
    "aw_element_tmp/domain3/playlist_page.png", "aw_element_tmp/domain3/sheet.png",
    "aw_element_tmp/domain3/volume_popup.png", "aw_element_tmp/domain3/final_home.png",
    "aw_element_tmp/domain3/final_state.png", "aw_element_tmp/domain3/after_gedan_click.png",
    "aw_element_tmp/domain3/after_login_fail.png", "aw_element_tmp/domain3/setup_unknown.png",
    "aw_element_tmp/domain3/loop_state_0.png", "aw_element_tmp/domain3/loop_state_1.png",
    "aw_element_tmp/domain3/loop_state_2.png", "aw_element_tmp/domain3/loop_state_3.png",
    # recap11 / recap12
    "aw_element_tmp/recap11/home_music.png", "aw_element_tmp/recap11/home_recommend.png",
    "aw_element_tmp/recap11/me.png", "aw_element_tmp/recap11/platform.png",
    "aw_element_tmp/recap11/sheet.png", "aw_element_tmp/recap11/history.png",
    "aw_element_tmp/recap11/final_home.png", "aw_element_tmp/recap11/current.png",
    "aw_element_tmp/recap12/ai.png", "aw_element_tmp/recap12/music.png",
    "aw_element_tmp/recap12/radio.png", "aw_element_tmp/recap12/recommend.png",
    "aw_element_tmp/recap12/vision.png", "aw_element_tmp/recap12/tab_ai.png",
    "aw_element_tmp/recap12/tab_music.png", "aw_element_tmp/recap12/tab_radio.png",
    "aw_element_tmp/recap12/tab_recommend.png", "aw_element_tmp/recap12/tab_vision.png",
    "aw_element_tmp/recap12/final_home.png",
    # aw_element_tmp root src_* (element capture sources, full screens)
    "aw_element_tmp/src_home_ai.png", "aw_element_tmp/src_home_music.png",
    "aw_element_tmp/src_home_radio.png", "aw_element_tmp/src_home_recommend.png",
    "aw_element_tmp/src_home_vision.png", "aw_element_tmp/src_me.png",
    "aw_element_tmp/src_person_info.png", "aw_element_tmp/src_profile_edit.png",
    "aw_element_tmp/src_area_code.png", "aw_element_tmp/src_avatar_popup.png",
    "aw_element_tmp/smoke_ai_role_settings_page.png",
    "aw_element_tmp/final_state.png",
    # castsheet
    "aw_element_tmp/castsheet/home.png", "aw_element_tmp/castsheet/sheet.png",
    "aw_element_tmp/castsheet/sheet_fresh.png",
]

def main():
    from paddleocr import PaddleOCR
    import PIL.Image as I
    ocr = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False)
    out, fails = {}, []
    for i, rel in enumerate(CANDIDATES):
        p = SRC / rel
        if not p.exists():
            fails.append((rel, "missing")); continue
        try:
            sz = I.open(p).size
            res = ocr.ocr(str(p), cls=False)
            lines = []
            if res and res[0]:
                for item in res[0]:
                    # paddleocr result format: [box, (text, conf)]
                    txt = item[1][0]
                    conf = float(item[1][1])
                    if conf >= 0.5:
                        lines.append(txt)
            text = "\n".join(lines)
            out[rel] = {"text": text, "n_lines": len(lines), "size": list(sz)}
        except Exception as e:
            fails.append((rel, repr(e)[:100]))
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{len(CANDIDATES)}", flush=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OCR done: {len(out)} ok, {len(fails)} fails -> {OUT}")
    for rel, err in fails:
        print("  FAIL", rel, err)

if __name__ == "__main__":
    main()
