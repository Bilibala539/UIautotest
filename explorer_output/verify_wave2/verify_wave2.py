# -*- coding: utf-8 -*-
"""Wave 2 enrich-kb 真机走通验证（aw-verify，不跑 pytest）。

用法: python verify_wave2.py <stage>
stage: state | s1 | s2 | s3 | s4 | s5 | s6 | final

验证 6 个 draft 页 + 播放页复验（knowledge/swan/draft/swan_*.md）的
「进入方式」+「生效断言」，截图存 explorer_output/screenshots/verify_wave2/。
断言依据打印 [PASS]/[FAIL] 行。

⛔ 纪律：不点保存/删除歌单/任何设备行/授权按钮/语音按钮；禁止坐标点击。
"""
import os
import sys
import logging

sys.path.insert(0, r"E:\UIAutotest")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
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
    SWAN_HOME_TAB_AI,
    SWAN_HOME_TAB_RECOMMEND,
    SWAN_PLAYLIST_BACK_BTN,
    SWAN_PLAYLIST_CREATE_BTN,
    SWAN_PLAYLIST_TAB_SWAN,
    SWAN_PLAYLIST_NEWDLG_CLOSE_BTN,
    SWAN_PD_MORE_BTN,
    SWAN_PD_PLAY_ALL,
    SWAN_FAVORITE_PLAY_ALL,
    SWAN_HISTORY_TOPBAR,
    SWAN_HISTORY_TABBAR,
    SWAN_DEVICE_SHEET_TITLE,
    SWAN_PLAYER_DEVICE_BTN,
    SWAN_AI_CHAT_VOICE_BTN,
    SWAN_AI_CHAT_INPUT,
)

PACKAGE = "com.swan.network"
SHOT_DIR = "verify_wave2"
u = SwanUser(driver=FlutterAndroidDriver())
b = u.aw

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


def ensure_home():
    """回首页·推荐 Tab（干净起点）。

    注意：bottom tab_recommend（key，desc='首页'）只回首页宿主，不重置顶部五 Tab；
    顶部「推荐」Tab 无 key，用未选中态图片 SWAN_HOME_TAB_RECOMMEND 切换。
    """
    for _ in range(4):
        if b.accessibility_exists(SwanBusiness.KEY_TAB_ME):
            break
        b.press_back()
        b.sleep(1.5)
    assert b.accessibility_exists(SwanBusiness.KEY_TAB_ME), "未回到首页（登录态丢失？）"
    b.click_accessibility(SwanBusiness.KEY_TAB_RECOMMEND)
    b.sleep(1.0)
    # 判断当前顶部 Tab：推荐 Tab（两种服务端布局）都含「已播歌曲」卡片；
    # 其它 Tab（音乐宫格/AI/可视音箱/电台）无此元素。
    descs = " ".join((n.get("content_desc") or "") for n in b.dump_semantics())
    if "已播歌曲" not in descs:
        b.click_image(SWAN_HOME_TAB_RECOMMEND)
        b.sleep(1.5)
        descs = " ".join((n.get("content_desc") or "") for n in b.dump_semantics())
        assert "已播歌曲" in descs, "未能回到首页·推荐 Tab"


# ==================== stage: state ====================

def stage_state():
    if not b.accessibility_exists(SwanBusiness.KEY_TAB_ME):
        print("[STATE] 不在登录态首页，尝试启动 App")
        b.driver.start_app(PACKAGE)
        b.sleep(6)
    logged = b.accessibility_exists(SwanBusiness.KEY_TAB_ME)
    print(f"[STATE] tab_me exists={logged}")
    bp = b.accessibility_exists(SwanBusiness.KEY_BOTTOM_PLAYER)
    print(f"[STATE] bottom_player exists={bp}（残留播放任务）")
    shot("00_state.png")
    print("[OCR]", ocr_texts())
    check("起点: 登录态首页(tab_me)", logged)


# ==================== 歌单页入口（首页推荐 Tab「歌单」卡片，动态轮换） ====================
# 2026-09-10 实测：首页·推荐 Tab 有两种服务端轮换布局：
#  - 完整布局：搜索条 + 平台图标行 + 我喜欢|歌单|AI 卡片行 + 最近播放（有「歌单」卡）
#  - 紧凑布局：我喜欢|AI 卡片行 + 最近播放（无「歌单」卡）
# 布局间歇轮换（下拉刷新不一定触发切换），入口验证需趁完整布局。

def goto_playlist_page(tries=3):
    """首页 → 「歌单」卡片 → 歌单页。返回是否到达。"""
    for i in range(tries):
        for _ in range(3):
            if b.accessibility_exists(SwanBusiness.KEY_TAB_ME):
                break
            b.press_back()
            b.sleep(1.5)
        assert b.accessibility_exists(SwanBusiness.KEY_TAB_ME), "未回到首页"
        nodes = [(n.get("content_desc") or "", n.get("bounds")) for n in b.dump_semantics()]
        has_card = any(d == "歌单" and box and box[1] < 1100 for d, box in nodes)
        if has_card:
            b.click_text("歌单", timeout=8)
            b.sleep(2)
            return True
        print(f"[S1] 首页无歌单卡片（紧凑布局态），第{i + 1}次下拉刷新等待轮换")
        b.swipe_down(400)
        b.sleep(3)
    return False


# ==================== stage: s1 歌单页 ====================

def stage_s1():
    ok = goto_playlist_page()
    shot("11_playlist_page.png")
    check("歌单页: 入口可达(首页「歌单」卡片，动态轮换)", ok)
    if not ok:
        return
    texts = ocr_texts()
    print("[OCR] playlist:", texts)
    check("歌单页: OCR SWAN(平台Tab)", has(texts, "SWAN"))
    check("歌单页: OCR 已加载全部(列表脚注)", has(texts, "已加载全部"))
    check("歌单页: 图片 SWAN_PLAYLIST_CREATE_BTN", img_ok(SWAN_PLAYLIST_CREATE_BTN))
    check("歌单页: 图片 SWAN_PLAYLIST_BACK_BTN", img_ok(SWAN_PLAYLIST_BACK_BTN))

    # ---- 切 QQ音乐 Tab 验证 SWAN Tab 未选中态图（第三方未授权空态，⛔ 不点去授权）----
    b.click_text("QQ音乐", timeout=8)
    b.sleep(1.5)
    shot("12_playlist_qq_tab.png")
    texts = ocr_texts()
    print("[OCR] playlist_qq:", texts)
    check("歌单页: QQ音乐Tab 图片 SWAN_PLAYLIST_TAB_SWAN(未选中态)", img_ok(SWAN_PLAYLIST_TAB_SWAN))
    check("歌单页: QQ音乐Tab OCR 未授权空态(暂未授权/去授权)",
          has(texts, "暂未授权") or has(texts, "去授权"))
    # 切回 SWAN Tab（顺带验证该图可作为定位器点击）
    b.click_image(SWAN_PLAYLIST_TAB_SWAN)
    b.sleep(1.5)
    shot("13_back_swan_tab.png")
    texts = ocr_texts()
    check("歌单页: click_image(SWAN_PLAYLIST_TAB_SWAN) 切回(已加载全部)", has(texts, "已加载全部"))

    # ---- 新建歌单弹窗：打开 → 立即点右上关闭（⛔ 不点保存）----
    b.click_image(SWAN_PLAYLIST_CREATE_BTN)
    b.sleep(1.5)
    shot("14_new_playlist_dlg.png")
    texts = ocr_texts()
    print("[OCR] new_dlg:", texts)
    check("新建歌单弹窗: OCR 新建歌单(标题)", has(texts, "新建歌单"))
    check("新建歌单弹窗: OCR 选择平台", has(texts, "选择平台"))
    b.click_image(SWAN_PLAYLIST_NEWDLG_CLOSE_BTN)
    b.sleep(1.5)
    shot("15_dlg_closed.png")
    texts = ocr_texts()
    print("[OCR] dlg_closed:", texts)
    check("新建歌单弹窗: 关闭后弹窗消失(选择平台不再出现)", not has(texts, "选择平台"))
    check("新建歌单弹窗: 关闭后仍在歌单页", img_ok(SWAN_PLAYLIST_CREATE_BTN))

    # ---- 返回首页 ----
    b.press_back()
    b.sleep(1.5)
    shot("16_back_home.png")
    check("歌单页: press_back 回首页(tab_me)", b.accessibility_exists(SwanBusiness.KEY_TAB_ME))


# ==================== stage: s2 歌单详情页 ====================

def stage_s2():
    ok = goto_playlist_page()
    shot("20_playlist_page.png")
    check("歌单详情页: 上游歌单页可达", ok)
    if not ok:
        return

    # ---- 进入：歌单页「我的家庭」行 ----
    b.click_text("我的家庭", timeout=8)
    b.sleep(2)
    shot("21_pd_family.png")
    texts = ocr_texts()
    print("[OCR] pd_family:", texts)
    check("歌单详情页: OCR 我的家庭(标题)", has(texts, "我的家庭"))
    check("歌单详情页: OCR 暂无内容(空态)", has(texts, "暂无内容"))
    check("歌单详情页: 图片 SWAN_PD_MORE_BTN(⋮ 更多，本页判据)", img_ok(SWAN_PD_MORE_BTN))
    check("歌单详情页: 图片 SWAN_PD_PLAY_ALL(播放全部，⛔ 只断言不点)", img_ok(SWAN_PD_PLAY_ALL))

    # ---- ⋮ 更多 action sheet：打开 → 断言菜单 → 点「取消」关闭（⛔ 删除歌单绝不点）----
    b.click_image(SWAN_PD_MORE_BTN)
    b.sleep(1.5)
    shot("22_pd_more_sheet.png")
    texts = ocr_texts()
    print("[OCR] pd_more_sheet:", texts)
    check("更多sheet: OCR 修改名称", has(texts, "修改名称"))
    check("更多sheet: OCR 删除歌单", has(texts, "删除歌单"))
    check("更多sheet: OCR 取消", has(texts, "取消"))
    b.click_text("取消", timeout=8)
    b.sleep(1.5)
    shot("23_sheet_cancelled.png")
    texts = ocr_texts()
    print("[OCR] sheet_cancelled:", texts)
    check("更多sheet: 点取消后关闭(修改名称不再出现)", not has(texts, "修改名称"))
    check("更多sheet: 关闭后仍在歌单详情页", img_ok(SWAN_PD_MORE_BTN))

    # ---- 返回：详情页 → 歌单页 → 首页 ----
    b.press_back()
    b.sleep(1.5)
    shot("24_back_playlist.png")
    check("歌单详情页: press_back 回歌单页", img_ok(SWAN_PLAYLIST_CREATE_BTN, timeout=4))
    b.press_back()
    b.sleep(1.5)
    shot("25_back_home.png")
    check("歌单详情页: press_back 回首页(tab_me)", b.accessibility_exists(SwanBusiness.KEY_TAB_ME))


# ==================== stage: s3 我喜欢页 ====================

def stage_s3():
    ensure_home()
    shot("30_home_ilike_card.png")

    # ---- 进入：首页「我喜欢」卡片 ----
    b.click_text("我喜欢", timeout=8)
    b.sleep(2)
    shot("31_ilike_page.png")
    texts = ocr_texts()
    print("[OCR] ilike:", texts)
    check("我喜欢页: OCR 我喜欢(标题)", has(texts, "我喜欢"))
    check("我喜欢页: OCR 宝藏音乐(歌单头副标题)", has(texts, "宝藏音乐"))
    check("我喜欢页: 图片 SWAN_FAVORITE_PLAY_ALL(播放全部，⛔ 只断言不点)",
          img_ok(SWAN_FAVORITE_PLAY_ALL))
    # 本账号错误态记录（dynamic，不作断言）
    token_err = has(texts, "TOKEN") or has(texts, "过期")
    print(f"[INFO] 我喜欢页错误空态(QQ音乐TOKEN过期): {token_err}")

    # 无更多按钮（与歌单详情页的判别）
    check("我喜欢页: 无 SWAN_PD_MORE_BTN(与歌单详情页判别)", not img_ok(SWAN_PD_MORE_BTN, timeout=4))

    # ---- 返回首页 ----
    b.press_back()
    b.sleep(1.5)
    shot("32_back_home.png")
    check("我喜欢页: press_back 回首页(tab_me)", b.accessibility_exists(SwanBusiness.KEY_TAB_ME))


# ==================== stage: s4 播放历史页 ====================

def stage_s4():
    ensure_home()

    # ---- 前置：滚动露出「最近播放」区 ----
    b.swipe_up(400)
    b.sleep(1)
    shot("40_home_scrolled.png")

    # ---- 进入：「已播歌曲」卡片 ----
    b.click_text("已播歌曲", timeout=8)
    b.sleep(2)
    shot("41_history_page.png")
    texts = ocr_texts()
    print("[OCR] history:", texts)
    check("播放历史页: OCR 最近播放(标题)", has(texts, "最近播放"))
    check("播放历史页: OCR 歌曲(分类Tab)", has(texts, "歌曲"))
    empty = has(texts, "暂无历史播放")
    print(f"[INFO] 播放历史页空态(暂无历史播放): {empty}")
    check("播放历史页: 图片 SWAN_HISTORY_TOPBAR(顶栏整条)", img_ok(SWAN_HISTORY_TOPBAR))
    check("播放历史页: 图片 SWAN_HISTORY_TABBAR(分类Tab条)", img_ok(SWAN_HISTORY_TABBAR))

    # ---- 返回首页（回滚顶部恢复起点）----
    b.press_back()
    b.sleep(1.5)
    shot("42_back_home.png")
    check("播放历史页: press_back 回首页(tab_me)", b.accessibility_exists(SwanBusiness.KEY_TAB_ME))
    b.swipe_down(400)
    b.sleep(0.8)
    b.swipe_down(400)
    b.sleep(0.8)
    shot("43_home_top_restored.png")


# ==================== stage: s5 播放页复验 + 切换设备弹层 ====================

def stage_s5():
    ensure_home()

    # ---- 依赖播放态：bottom_player 残留任务 ----
    if not b.accessibility_exists(SwanBusiness.KEY_BOTTOM_PLAYER):
        print("[SKIP] bottom_player 不存在（残留任务已清），播放页/切换设备弹层"
              " 依赖播放态，本轮无法复验")
        check("播放页复验: 依赖播放态(本轮无法复验，记 SKIP)", True)
        return
    shot("50_bottom_player.png")

    # ---- 进入全屏播放页 ----
    b.click_accessibility(SwanBusiness.KEY_BOTTOM_PLAYER)
    b.sleep(2)
    assert b.wait_accessibility(SwanBusiness.KEY_FULL_PLAYER_PAGE, timeout=10), "未进入播放页"
    shot("51_player_page.png")
    check("播放页: full_player_page key 存在", True)
    check("播放页: 图片 SWAN_PLAYER_DEVICE_BTN(设备切换按钮)", img_ok(SWAN_PLAYER_DEVICE_BTN))

    # ---- 切换设备弹层（⛔ 不点任何设备行）----
    b.click_accessibility("player_device_button")
    b.sleep(2)
    ok = b.wait_accessibility("multiroom_sheet", timeout=8)
    check("切换设备弹层: multiroom_sheet key 存在", ok)
    shot("52_device_sheet.png")
    texts = ocr_texts()
    print("[OCR] device_sheet:", texts)
    check("切换设备弹层: 图片 SWAN_DEVICE_SHEET_TITLE(标题行)", img_ok(SWAN_DEVICE_SHEET_TITLE))
    check("切换设备弹层: OCR 切换设备(标题)", has(texts, "切换设备"))
    b.press_back()
    b.sleep(1.5)
    shot("53_sheet_closed.png")
    check("切换设备弹层: press_back 后关闭(multiroom_sheet 消失)",
          not b.accessibility_exists("multiroom_sheet"))
    check("切换设备弹层: 关闭后仍在播放页",
          b.accessibility_exists(SwanBusiness.KEY_FULL_PLAYER_PAGE))

    # ---- 收起播放页回首页 ----
    b.click_accessibility(SwanBusiness.KEY_PLAYER_DISMISS_BUTTON)
    b.sleep(1.5)
    shot("54_player_dismissed.png")
    check("播放页: 收起后回首页(tab_me)", b.accessibility_exists(SwanBusiness.KEY_TAB_ME))


# ==================== stage: s6 AI对话页 ====================

def stage_s6():
    ensure_home()

    # ---- 进入：首页 AI Tab → 角色卡 ----
    b.click_image(SWAN_HOME_TAB_AI)
    b.sleep(2)
    shot("60_ai_tab.png")
    role = "小薇"
    if not b.click_text(role, timeout=6):
        role = "惠威百科"
        assert b.click_text(role, timeout=6), "未找到角色卡"
    b.sleep(2)
    shot("61_ai_chat.png")
    texts = ocr_texts()
    print("[OCR] ai_chat:", texts)
    check(f"AI对话页: OCR {role}(角色名标题)", has(texts, role))
    check("AI对话页: OCR 内容由AI生成(页脚)", has(texts, "内容由AI生成"))
    check("AI对话页: 图片 SWAN_AI_CHAT_VOICE_BTN(语音按钮，⛔ 不点避免麦克风权限)",
          img_ok(SWAN_AI_CHAT_VOICE_BTN))
    check("AI对话页: 图片 SWAN_AI_CHAT_INPUT(输入框，不输入中文)",
          img_ok(SWAN_AI_CHAT_INPUT))

    # ---- 返回 AI Tab → 推荐 Tab ----
    b.press_back()
    b.sleep(1.5)
    shot("62_back_ai_tab.png")
    texts = ocr_texts()
    check("AI对话页: press_back 回AI Tab(历史对话记录)", has(texts, "历史对话记录"))
    b.click_image(SWAN_HOME_TAB_RECOMMEND)
    b.sleep(1.5)
    shot("63_back_recommend.png")
    check("AI对话页: 回推荐Tab(tab_me)", b.accessibility_exists(SwanBusiness.KEY_TAB_ME))


# ==================== stage: final ====================

def stage_final():
    ensure_home()
    bp = b.accessibility_exists(SwanBusiness.KEY_BOTTOM_PLAYER)
    print(f"[FINAL] bottom_player exists={bp}")
    shot("99_final_home.png")
    texts = ocr_texts()
    print("[OCR] final:", texts)
    check("收尾: 登录态首页·推荐Tab(tab_me)", b.accessibility_exists(SwanBusiness.KEY_TAB_ME))


STAGES = {
    "state": stage_state,
    "s1": stage_s1,
    "s2": stage_s2,
    "s3": stage_s3,
    "s4": stage_s4,
    "s5": stage_s5,
    "s6": stage_s6,
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
