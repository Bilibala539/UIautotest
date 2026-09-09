"""enrich-kb 导航验证（aw-verify 独立复验，不跑 pytest）。

用法: python verify_stages.py <stage>
stage: state | fav | help | about | pw | final
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

SHOT_DIR = "verify_explore2"
u = SwanUser(driver=FlutterAndroidDriver())
b = u.aw
PHONE = os.environ.get("SWAN_PHONE", "").strip()


def shot(name):
    p = b.screenshot_for_explore(filename=name, subdir=SHOT_DIR)
    print(f"[SHOT] {p}")
    return p


def ocr_texts():
    return [i["text"] for i in b.ocr_scan_page()]


def check(label, cond, extra=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {label} {extra}")
    return bool(cond)


def has(texts, sub):
    return any(sub in t for t in texts)


def goto_me():
    """从任意 tab 页回我的页（先点首页 tab 再点我的 tab，保证起点干净）。"""
    b.click_accessibility(b.KEY_TAB_RECOMMEND)
    b.sleep(1)
    b.click_accessibility(b.KEY_TAB_ME)
    b.sleep(1)
    # 我的页可能停留在滚动位置（顶部账号入口离屏），先滚回顶部
    for _ in range(3):
        if b.accessibility_exists(b.KEY_ME_PROFILE_ENTRY):
            break
        b.swipe_down(400)
        b.sleep(0.8)
    assert b.wait_accessibility(b.KEY_ME_PROFILE_ENTRY, timeout=10), "未进入我的页"


def stage_state():
    logged = b.accessibility_exists(b.KEY_TAB_ME)
    print(f"[STATE] tab_me exists={logged}")
    shot("00_state.png")
    print("[OCR]", ocr_texts())


def stage_fav():
    goto_me()
    shot("10_me.png")
    assert b.text_exists("SWAN收藏", timeout=5), "我的页未见 SWAN收藏 入口"
    b.click_text("SWAN收藏")
    b.sleep(1.5)
    shot("11_favorites.png")
    texts = ocr_texts()
    print("[OCR] favorites:", texts)
    ok_fav = check("收藏页判据(SWAN收藏+我的音乐/添加新的收藏歌单)",
                   has(texts, "SWAN收藏") or has(texts, "添加新的收藏歌单") or has(texts, "我的音乐"))
    assert ok_fav, "未到达 SWAN收藏 页"
    b.click_text("我的家庭")
    b.sleep(1.5)
    shot("12_group_detail.png")
    texts = ocr_texts()
    print("[OCR] group_detail:", texts)
    check("播放全部/首歌 命中", has(texts, "播放全部") or has(texts, "首歌"))
    for tab in ["全部", "QQ音乐", "网易云音乐", "酷狗音乐"]:
        check(f"来源筛选tab[{tab}]", has(texts, tab))
    # press_back 一次应回收藏页
    b.press_back()
    b.sleep(1.5)
    shot("13_after_back1.png")
    texts = ocr_texts()
    print("[OCR] after_back1:", texts)
    back_fav = check("press_back一次回收藏页(添加新的收藏歌单/我的音乐/SWAN收藏)",
                     has(texts, "添加新的收藏歌单") or has(texts, "我的音乐") or has(texts, "SWAN收藏"))
    if not back_fav:
        # 再按一次看落点，供报告判断 explorer"一次"结论真伪
        b.press_back()
        b.sleep(1.5)
        shot("14_after_back2.png")
        print("[OCR] after_back2:", ocr_texts())
        print("[FAIL] press_back 一次未回收藏页（已附第二次 back 落点）")
        return
    # 再退回我的页
    b.press_back()
    b.sleep(1.5)
    check("回到我的页", b.wait_accessibility(b.KEY_ME_PROFILE_ENTRY, timeout=10))


def stage_help():
    goto_me()
    b.swipe_up(400)
    b.sleep(0.8)
    b.swipe_up(400)
    b.sleep(0.8)
    shot("20_me_scrolled.png")
    b.click_text("帮助与反馈")
    b.sleep(1.5)
    shot("21_help.png")
    texts = ocr_texts()
    print("[OCR] help:", texts)
    check("标题[帮助与反馈]", has(texts, "帮助与反馈"))
    check("[使用说明]", has(texts, "使用说明"))
    check("[常见问题]", has(texts, "常见问题"))
    b.press_back()
    b.sleep(1.5)
    shot("22_help_back.png")
    # press_back 后回我的页，但可能停留在滚动位置（账号入口离屏），滚回顶部再判
    for _ in range(3):
        if b.accessibility_exists(b.KEY_ME_PROFILE_ENTRY):
            break
        b.swipe_down(400)
        b.sleep(0.8)
    check("press_back回我的页", b.wait_accessibility(b.KEY_ME_PROFILE_ENTRY, timeout=10))


def stage_about():
    goto_me()
    b.swipe_up(400)
    b.sleep(0.8)
    b.swipe_up(400)
    b.sleep(0.8)
    b.click_text("关于与升级")
    b.sleep(1.5)
    shot("23_about.png")
    texts = ocr_texts()
    print("[OCR] about:", texts)
    check("标题[关于与升级]", has(texts, "关于与升级"))
    check("[关于我们]", has(texts, "关于我们"))
    check("[软件升级]", has(texts, "软件升级"))
    check("版本号 5.3.0", has(texts, "5.3.0"))
    b.press_back()
    b.sleep(1.5)
    shot("24_about_back.png")
    for _ in range(3):
        if b.accessibility_exists(b.KEY_ME_PROFILE_ENTRY):
            break
        b.swipe_down(400)
        b.sleep(0.8)
    check("press_back回我的页", b.wait_accessibility(b.KEY_ME_PROFILE_ENTRY, timeout=10))
    b.go_home()


def _login_key_ids():
    ids = []
    for node in b.dump_semantics():
        nid = (node.get("resource_id") or "").split("/")[-1]
        if nid.startswith("login") and nid not in ids:
            ids.append(nid)
    return ids


def stage_pw():
    b.go_home()
    b.logout_if_needed()  # 首页→我的→个人信息→退出登入，落登录页
    b.sleep(1)
    shot("30_sms_login.png")
    # 出发前互斥性（验证码页一侧）：密码框不应存在
    pre_pw = b.accessibility_exists(b.KEY_PASSWORD_FIELD)
    pre_upw = b.accessibility_exists(b.KEY_USE_PASSWORD_BUTTON)
    check("验证码页: login_use_password_button 存在", pre_upw)
    check("验证码页: login_password_field 不存在(互斥)", not pre_pw)
    b.click_accessibility(b.KEY_USE_PASSWORD_BUTTON)
    b.sleep(1.5)
    shot("31_password_page.png")
    r_pw = b.accessibility_exists("login_password_field")
    r_sms = b.accessibility_exists("login_use_sms_button")
    r_upw = b.accessibility_exists("login_use_password_button")
    ids = _login_key_ids()
    print("[KEYS] password页 login* keys:", ids)
    check("login_password_field 存在", r_pw)
    check("login_use_sms_button 存在", r_sms)
    check("login_use_password_button 不存在(互斥)", not r_upw)
    texts = ocr_texts()
    print("[OCR] password_page:", texts)
    check("OCR占位[请输入密码]", has(texts, "请输入密码"))
    # 切回验证码页
    b.click_accessibility(b.KEY_USE_SMS_BUTTON if hasattr(b, "KEY_USE_SMS_BUTTON") else "login_use_sms_button")
    b.sleep(1.5)
    shot("32_back_to_sms.png")
    back_upw = b.accessibility_exists(b.KEY_USE_PASSWORD_BUTTON)
    back_pw = b.accessibility_exists("login_password_field")
    check("切回验证码页: login_use_password_button 重现", back_upw)
    check("切回验证码页: login_password_field 消失", not back_pw)
    # 重新登录恢复登录态
    b.login_by_sms(PHONE)
    b.sleep(1)
    shot("33_relogin_home.png")
    check("重新登录进入首页(tab_me)", b.wait_accessibility(b.KEY_TAB_ME, timeout=10))
    b.go_home()


def stage_final():
    check("登录态(tab_me)", b.accessibility_exists(b.KEY_TAB_ME))
    b.go_home()
    b.sleep(1)
    shot("99_final_home.png")
    print("[OCR] final:", ocr_texts())


STAGES = {
    "state": stage_state,
    "fav": stage_fav,
    "help": stage_help,
    "about": stage_about,
    "pw": stage_pw,
    "final": stage_final,
}

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "state"
    print(f"===== STAGE {name} =====")
    STAGES[name]()
    print(f"===== STAGE {name} DONE =====")
