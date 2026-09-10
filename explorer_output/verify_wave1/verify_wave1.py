# -*- coding: utf-8 -*-
"""Wave 1 enrich-kb 真机走通验证（aw-verify，不跑 pytest）。

用法: python verify_wave1.py <stage>
stage: state | tabs | profile | scan | areacode | final

验证 7 个 draft 页面（knowledge/swan/draft/swan_*.md）的「进入方式」+「生效断言」，
截图存 explorer_output/verify_wave1/。断言依据打印 [PASS]/[FAIL] 行。
"""
import os
import sys
import logging

sys.path.insert(0, r"E:\UIAutotest")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

from dotenv import load_dotenv
load_dotenv(r"E:\UIAutotest\.env")
load_dotenv(r"E:\UIAutotest\.env.local")
os.environ.setdefault("PLATFORM", "flutter")
os.environ.setdefault("ANDROID_DEVICE_SERIAL", "c0614b6a")

from utils.aw.driver.flutter_driver import FlutterAndroidDriver
from utils.user import SwanUser
from utils.aw.business.swan import SwanBusiness
from image.image_name_mapping import (
    SWAN_HOME_TAB_RECOMMEND,
    SWAN_HOME_TAB_MUSIC,
    SWAN_HOME_TAB_RADIO,
    SWAN_HOME_TAB_AI,
    SWAN_HOME_TAB_VISION,
    SWAN_HOME_MUSIC_SEARCH_BAR,
    SWAN_HOME_RADIO_SEARCH_BAR,
    SWAN_HOME_AI_ADD_ROLE,
    SWAN_HOME_AI_ROLE_SETTINGS,
    SWAN_HOME_VISION_UNBOUND_HINT,
    SWAN_ME_SCAN_ICON,
    SWAN_PROFILE_EDIT_DONE,
    SWAN_PROFILE_EDIT_AVATAR_CANCEL,
    SWAN_AREA_CODE_CHINA_ROW,
)

SHOT_DIR = "verify_wave1"
u = SwanUser(driver=FlutterAndroidDriver())
b = u.aw
PHONE = os.environ.get("SWAN_PHONE", "").strip()
PASSWORD = os.environ.get("SWAN_PASSWORD", "").strip()

RESULTS = []


def shot(name):
    p = b.screenshot_for_explore(filename=name, subdir=SHOT_DIR)
    print(f"[SHOT] {p}")
    return p


def ocr_texts():
    return [i["text"] for i in b.ocr_scan_page()]


def check(label, cond, extra=""):
    cond = bool(cond)
    RESULTS.append((label, cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {label} {extra}")
    return cond


def has(texts, sub):
    return any(sub in t for t in texts)


def img_ok(name, timeout=6):
    """非断言版图片存在性（find_image 失败返回 None 不抛）"""
    return b.find_image(name, timeout=timeout) is not None


def goto_me():
    """从任意页回我的页（先首页 tab 再我的 tab），滚回顶部保证账号入口可见。"""
    b.click_accessibility(SwanBusiness.KEY_TAB_RECOMMEND)
    b.sleep(1)
    b.click_accessibility(SwanBusiness.KEY_TAB_ME)
    b.sleep(1)
    for _ in range(3):
        if b.accessibility_exists(SwanBusiness.KEY_ME_PROFILE_ENTRY):
            break
        b.swipe_down(400)
        b.sleep(0.8)
    assert b.wait_accessibility(SwanBusiness.KEY_ME_PROFILE_ENTRY, timeout=10), "未进入我的页"


# ==================== stage: state ====================

def stage_state():
    logged = b.accessibility_exists(SwanBusiness.KEY_TAB_ME)
    print(f"[STATE] tab_me exists={logged}")
    shot("00_state.png")
    print("[OCR]", ocr_texts())


# ==================== stage: tabs（音乐/电台/AI/可视音箱 4 页） ====================

def stage_tabs():
    assert b.wait_accessibility(SwanBusiness.KEY_TAB_ME, timeout=10), "起点不在首页"
    shot("10_start_recommend.png")

    # ---- 1. 音乐 Tab ----
    b.click_image(SWAN_HOME_TAB_MUSIC)
    b.sleep(2)
    shot("11_music_tab.png")
    texts = ocr_texts()
    print("[OCR] music:", texts)
    check("音乐Tab: OCR 跨平台搜索音乐", has(texts, "跨平台搜索音乐"))
    check("音乐Tab: OCR QQ音乐", has(texts, "QQ音乐"))
    check("音乐Tab: 图片 SWAN_HOME_MUSIC_SEARCH_BAR", img_ok(SWAN_HOME_MUSIC_SEARCH_BAR))
    check("音乐Tab: 图片 SWAN_HOME_TAB_RECOMMEND(未选中态)", img_ok(SWAN_HOME_TAB_RECOMMEND))

    # ---- 2. 电台 Tab ----
    b.click_image(SWAN_HOME_TAB_RADIO)
    b.sleep(2)
    shot("12_radio_tab.png")
    texts = ocr_texts()
    print("[OCR] radio:", texts)
    check("电台Tab: OCR 搜索电台", has(texts, "搜索电台"))
    check("电台Tab: OCR 全国电台", has(texts, "全国电台"))
    check("电台Tab: 图片 SWAN_HOME_RADIO_SEARCH_BAR", img_ok(SWAN_HOME_RADIO_SEARCH_BAR))

    # ---- 3. AI Tab ----
    b.click_image(SWAN_HOME_TAB_AI)
    b.sleep(2)
    shot("13_ai_tab.png")
    texts = ocr_texts()
    print("[OCR] ai:", texts)
    check("AITab: OCR 添加更多AI角色", has(texts, "添加更多AI角色"))
    check("AITab: OCR 历史对话记录", has(texts, "历史对话记录"))
    check("AITab: 图片 SWAN_HOME_AI_ADD_ROLE", img_ok(SWAN_HOME_AI_ADD_ROLE))
    check("AITab: 图片 SWAN_HOME_AI_ROLE_SETTINGS", img_ok(SWAN_HOME_AI_ROLE_SETTINGS))

    # ---- 4. 可视音箱 Tab ----
    b.click_image(SWAN_HOME_TAB_VISION)
    b.sleep(2)
    shot("14_vision_tab.png")
    texts = ocr_texts()
    print("[OCR] vision:", texts)
    check("可视音箱Tab: OCR 暂未添加可视音箱", has(texts, "暂未添加可视音箱"))
    check("可视音箱Tab: OCR 添加可视音响", has(texts, "添加可视音响"))
    check("可视音箱Tab: 图片 SWAN_HOME_VISION_UNBOUND_HINT", img_ok(SWAN_HOME_VISION_UNBOUND_HINT))

    # ---- 回推荐 Tab（顺带验证 SWAN_HOME_TAB_RECOMMEND click） ----
    b.click_image(SWAN_HOME_TAB_RECOMMEND)
    b.sleep(2)
    shot("15_back_recommend.png")
    check("回首页·推荐Tab(tab_me 仍在)", b.accessibility_exists(SwanBusiness.KEY_TAB_ME))
    texts = ocr_texts()
    print("[OCR] recommend:", texts)


# ==================== stage: profile（资料编辑页） ====================

def stage_profile():
    goto_me()
    shot("20_me.png")
    # 进个人信息页
    b.click_accessibility(SwanBusiness.KEY_ME_PROFILE_ENTRY)
    assert b.wait_accessibility(SwanBusiness.KEY_PERSON_INFO_PAGE, timeout=10), "未进入个人信息页"
    shot("21_person_info.png")

    # ---- 修改昵称页 ----
    b.click_text("昵称")
    b.sleep(2)
    shot("22_edit_nickname.png")
    texts = ocr_texts()
    print("[OCR] edit_nickname:", texts)
    check("修改昵称页: OCR 修改昵称", has(texts, "修改昵称"))
    check("修改昵称页: 图片 SWAN_PROFILE_EDIT_DONE(完成按钮)", img_ok(SWAN_PROFILE_EDIT_DONE))
    # 返回：键盘弹出时第一次收键盘，第二次回个人信息页
    for i in range(3):
        if b.accessibility_exists(SwanBusiness.KEY_PERSON_INFO_PAGE):
            break
        b.press_back()
        b.sleep(1.5)
    check("修改昵称页: press_back 回个人信息页",
          b.accessibility_exists(SwanBusiness.KEY_PERSON_INFO_PAGE))

    # ---- 头像弹层（不点拍照/相册，点取消关闭） ----
    b.click_text("头像")
    b.sleep(2)
    shot("23_avatar_sheet.png")
    texts = ocr_texts()
    print("[OCR] avatar_sheet:", texts)
    check("头像弹层: OCR 从手机相册选取", has(texts, "从手机相册选取"))
    b.click_image(SWAN_PROFILE_EDIT_AVATAR_CANCEL)
    b.sleep(1.5)
    shot("24_avatar_cancelled.png")
    texts = ocr_texts()
    check("头像弹层: click_image 取消后弹层关闭", not has(texts, "从手机相册选取"))
    check("头像弹层: 关闭后仍在个人信息页",
          b.accessibility_exists(SwanBusiness.KEY_PERSON_INFO_PAGE))

    # ⚠️ 不进修改密码页（FLAG_SECURE 防截屏）。收尾：回我的页 → 首页
    b.press_back()
    b.sleep(1.5)
    shot("25_back_me.png")
    check("press_back 回我的页", b.accessibility_exists(SwanBusiness.KEY_ME_PROFILE_ENTRY))
    b.go_home()


# ==================== stage: scan（扫一扫页） ====================

def stage_scan():
    goto_me()
    shot("30_me.png")
    b.click_image(SWAN_ME_SCAN_ICON)
    b.sleep(1.5)
    # 首次进入相机权限弹窗（explorer 曾拒绝过，可能不再出现）
    if b.accessibility_exists("permission_allow_one_time_button"):
        print("[INFO] 相机权限弹窗出现，点「仅本次使用时允许」")
        shot("31_camera_permission.png")
        b.click_accessibility("permission_allow_one_time_button")
        b.sleep(2)
    else:
        print("[INFO] 相机权限弹窗未出现（此前已授权/会话内已允许），直接断言页面")
    shot("32_scan_page.png")
    texts = ocr_texts()
    print("[OCR] scan:", texts)
    check("扫一扫页: OCR 扫一扫(标题)", has(texts, "扫一扫"))
    # 测试机相机硬件不可用 → 错误态属正常（不反复重试）
    check("扫一扫页: 相机不可用错误态(OCR 相机不可用/重试)",
          has(texts, "相机不可用") or has(texts, "重试"))
    # 返回我的页 → 首页
    b.press_back()
    b.sleep(1.5)
    shot("33_back_me.png")
    check("press_back 回我的页", b.accessibility_exists(SwanBusiness.KEY_ME_PROFILE_ENTRY))
    b.go_home()


# ==================== stage: areacode（区号选择页，最后做） ====================

def stage_areacode():
    b.go_home()
    b.logout_if_needed()  # 首页→我的→个人信息→退出登入，落登录页
    b.sleep(1.5)
    shot("40_login_page.png")
    check("登出后到登录页(login_area_code_button 存在)",
          b.accessibility_exists(SwanBusiness.KEY_AREA_CODE_BUTTON))

    # ---- 区号选择页 ----
    b.click_accessibility(SwanBusiness.KEY_AREA_CODE_BUTTON)
    b.sleep(2)
    shot("41_area_code_page.png")
    texts = ocr_texts()
    print("[OCR] area_code:", texts)
    check("区号选择页: OCR 选择归属地", has(texts, "选择归属地"))
    check("区号选择页: OCR 中国香港(热门组已加载)", has(texts, "中国香港"))

    # ---- 点「中国 +86」行，断言自动返回登录页 ----
    b.click_image(SWAN_AREA_CODE_CHINA_ROW)
    b.sleep(2)
    shot("42_after_china_row.png")
    check("选中国行后返回登录页(login_page)",
          b.wait_accessibility(SwanBusiness.KEY_LOGIN_PAGE, timeout=10))
    # 区号按钮 desc 应为 +86
    desc = ""
    for node in b.dump_semantics():
        nid = (node.get("resource_id") or "").split("/")[-1]
        if nid == "login_area_code_button":
            desc = node.get("content_desc") or node.get("text") or ""
            break
    check("选中国行后区号按钮 desc=+86", "+86" in desc, f"desc={desc!r}")

    # ---- 重新登录恢复标准起点 ----
    b.login_with_password(PHONE, PASSWORD)
    b.sleep(1.5)
    shot("43_relogin_home.png")
    check("重新登录进首页(tab_me)", b.accessibility_exists(SwanBusiness.KEY_TAB_ME))
    # 点回推荐 Tab（登出前顶部 Tab 停留态不保证）
    b.click_accessibility(SwanBusiness.KEY_TAB_RECOMMEND)
    b.sleep(1)
    shot("44_final_recommend.png")


# ==================== stage: final ====================

def stage_final():
    check("登录态(tab_me)", b.accessibility_exists(SwanBusiness.KEY_TAB_ME))
    b.click_accessibility(SwanBusiness.KEY_TAB_RECOMMEND)
    b.sleep(1)
    shot("99_final_home.png")
    texts = ocr_texts()
    print("[OCR] final:", texts)


STAGES = {
    "state": stage_state,
    "tabs": stage_tabs,
    "profile": stage_profile,
    "scan": stage_scan,
    "areacode": stage_areacode,
    "final": stage_final,
}

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "state"
    print(f"===== STAGE {name} =====")
    try:
        STAGES[name]()
    finally:
        n_pass = sum(1 for _, ok in RESULTS if ok)
        print(f"===== STAGE {name} SUMMARY: {n_pass}/{len(RESULTS)} PASS =====")
        for label, ok in RESULTS:
            print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
