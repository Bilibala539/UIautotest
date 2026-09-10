# -*- coding: utf-8 -*-
"""aw-element Wave2 元素源图采集脚本（歌单/歌单详情/我喜欢/播放历史/AI对话/播放页）。

通过 AW 层（SwanUser/FlutterAndroidDriver）导航真机并截整页图，
保存到 explorer_output/aw_element_tmp/wave2/ 供裁剪与离线匹配校验。
用法：venv/Scripts/python.exe explorer_output/aw_element_tmp/wave2/capture2.py <stage>
stage: state | playlist | favorite_history | ai_chat | player
"""
from __future__ import annotations

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

OUT = r"E:\UIAutotest\explorer_output\aw_element_tmp\wave2"

TOP_TAB_REGION = (0, 60, 720, 200)   # 首页顶 Tab 行
TOPBAR_REGION = (0, 60, 720, 230)    # 二级页顶栏（返回+标题+右上图标）


def make_user() -> SwanUser:
    return SwanUser(driver=FlutterAndroidDriver())


def shot(aw, name: str) -> None:
    path = os.path.join(OUT, name)
    aw.take_screenshot(save_path=path)
    print(f"[shot] {name}")


def dump_nodes(aw, label: str, y_max: int = 320) -> None:
    """打印屏幕上部语义节点（辅助定位无文案图标）并保存全量到文件。"""
    dump_all(aw, label + f"_top{y_max}")
    print(f"--- nodes y<{y_max} @ {label} ---")
    for n in aw.dump_semantics():
        b = n.get("bounds")
        if not b:
            continue
        x1, y1, x2, y2 = b
        if y2 <= y_max:
            print(_fmt_node(n))


def _fmt_node(n) -> str:
    b = n.get("bounds")
    rid = (n.get("resource_id") or "").split("/")[-1]
    label_txt = n.get("text") or n.get("content_desc")
    box = f"({b[0]},{b[1]})-({b[2]},{b[3]})" if b else "?"
    return (f"  id={rid!r} txt={label_txt!r} cls={n.get('class_name','')!r} "
            f"click={n.get('clickable')} box={box}")


def dump_all(aw, label: str) -> None:
    """打印全部语义节点并保存到 OUT/<label>_nodes.txt。"""
    print(f"--- all nodes @ {label} ---")
    lines = [f"--- all nodes @ {label} ---"]
    for n in aw.dump_semantics():
        line = _fmt_node(n)
        lines.append(line)
    with open(os.path.join(OUT, f"{label}_nodes.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[dump] {label}_nodes.txt ({len(lines)-1} nodes)")


def click_icon_by_dump(aw, x1, y1, x2, y2, label: str) -> None:
    """按语义 dump 动态找区域内的 clickable 节点并点其中心（探索期定位无文案图标）。

    坐标只作为节点筛选窗口（非固化点击坐标），找不到即抛错。
    """
    for n in aw.dump_semantics():
        b = n.get("bounds")
        if not b or not n.get("clickable"):
            continue
        nx1, ny1, nx2, ny2 = b
        if nx1 >= x1 and ny1 >= y1 and nx2 <= x2 and ny2 <= y2:
            cx, cy = (nx1 + nx2) // 2, (ny1 + ny2) // 2
            print(f"[icon] {label}: node {b} -> tap center ({cx},{cy})")
            assert aw.tap(cx, cy)
            return
    raise AssertionError(f"[icon] {label}: 区域 ({x1},{y1})-({x2},{y2}) 内无 clickable 节点")


def go_home_recommend(aw) -> None:
    """回到首页·推荐 Tab（顶 Tab 持久化，须显式点「推荐」）。"""
    assert aw.wait_accessibility(SB.KEY_TAB_ME, timeout=15), "不在首页（tab_me 未出现）"
    time.sleep(1.0)
    assert aw.click_text("推荐", region=TOP_TAB_REGION), "点顶 Tab「推荐」失败"
    time.sleep(1.5)


def stage_state() -> None:
    user = make_user()
    aw = user.aw
    print("tab_me:", aw.accessibility_exists(SB.KEY_TAB_ME))
    print("bottom_player:", aw.accessibility_exists(SB.KEY_BOTTOM_PLAYER))
    dump_nodes(aw, "current", y_max=1600)
    shot(aw, "state_check.png")


def stage_playlist() -> None:
    """歌单页（含 QQ音乐 Tab 态、新建歌单弹窗）+ 歌单详情页。"""
    user = make_user()
    aw = user.aw
    go_home_recommend(aw)

    # 1) 进歌单页
    assert aw.click_text("歌单", region=(0, 200, 720, 1100)), "点首页「歌单」卡片失败"
    time.sleep(2.0)
    assert aw.text_exists("SWAN", region=(0, 60, 720, 320)), "歌单页未出现 SWAN Tab"
    dump_nodes(aw, "playlist", y_max=340)
    shot(aw, "src_playlist.png")

    # 2) 切 QQ音乐 Tab，截 SWAN 未选中态
    assert aw.click_text("QQ音乐", region=(0, 180, 720, 300)), "点「QQ音乐」Tab 失败"
    time.sleep(2.0)
    shot(aw, "src_playlist_qq.png")
    # 切回 SWAN
    assert aw.click_text("SWAN", region=(0, 180, 720, 300)), "点回「SWAN」Tab 失败"
    time.sleep(2.0)

    # 3) 点右上新建图标 → 弹窗 → 立即点右上关闭（不点保存）
    click_icon_by_dump(aw, 560, 60, 720, 200, "歌单页-新建歌单图标")
    time.sleep(1.5)
    assert aw.text_exists("新建歌单", region=(0, 150, 720, 400)), "新建歌单弹窗未出现"
    dump_nodes(aw, "playlist_newdlg", y_max=800)
    shot(aw, "src_playlist_newdlg.png")
    click_icon_by_dump(aw, 520, 200, 720, 330, "新建歌单弹窗-关闭按钮")
    time.sleep(1.5)
    assert aw.text_exists("SWAN", region=(0, 60, 720, 320)), "关闭弹窗后未回到歌单页"

    # 4) 点「我的家庭」歌单行 → 歌单详情页
    assert aw.click_text("我的家庭", region=(0, 300, 720, 1000)), "点「我的家庭」歌单行失败"
    time.sleep(2.0)
    assert aw.text_exists("播放全部", timeout=10), "歌单详情页未出现「播放全部」"
    dump_nodes(aw, "playlist_detail", y_max=700)
    shot(aw, "src_playlist_detail.png")
    # 返回歌单页 → 返回首页
    aw.press_back()
    time.sleep(1.5)
    aw.press_back()
    time.sleep(1.5)
    print("[stage playlist] done，已回首页")


def stage_favorite_history() -> None:
    """我喜欢页 + 播放历史页。"""
    user = make_user()
    aw = user.aw
    go_home_recommend(aw)

    # 1) 我喜欢页
    assert aw.click_text("我喜欢", region=(0, 200, 720, 1100)), "点首页「我喜欢」卡片失败"
    time.sleep(2.0)
    assert aw.text_exists("宝藏音乐", timeout=10), "我喜欢页副标题未出现"
    dump_nodes(aw, "favorite", y_max=700)
    shot(aw, "src_favorite.png")
    aw.press_back()
    time.sleep(1.5)

    # 2) 播放历史页：swipe_up 露出「已播歌曲」卡片
    assert aw.wait_accessibility(SB.KEY_TAB_ME, timeout=10), "未回到首页"
    aw.swipe_up(distance=500)
    time.sleep(1.5)
    assert aw.click_text("已播歌曲", timeout=10), "点「已播歌曲」卡片失败"
    time.sleep(2.0)
    assert aw.text_exists("最近播放", timeout=10), "播放历史页标题未出现"
    dump_nodes(aw, "history", y_max=400)
    shot(aw, "src_history.png")
    aw.press_back()
    time.sleep(1.5)
    print("[stage favorite_history] done，已回首页")


def stage_ai_chat() -> None:
    """AI 对话页（只截图，不点语音按钮避免权限弹窗）。"""
    user = make_user()
    aw = user.aw
    assert aw.wait_accessibility(SB.KEY_TAB_ME, timeout=15), "不在首页"
    time.sleep(1.0)
    assert aw.click_text("AI", region=TOP_TAB_REGION), "点顶 Tab「AI」失败"
    time.sleep(2.0)
    assert aw.click_text("小薇", timeout=10, region=(0, 200, 720, 1300)), "点角色卡「小薇」失败"
    time.sleep(2.5)
    assert aw.text_exists("内容由AI生成", timeout=10), "AI 对话页页脚未出现"
    dump_all(aw, "ai_chat")
    shot(aw, "src_ai_chat.png")
    aw.press_back()
    time.sleep(1.5)
    print("[stage ai_chat] done，已回 AI Tab")


def stage_player() -> None:
    """播放页 + 切换设备弹层（bottom_player 无播放任务时跳过）。"""
    user = make_user()
    aw = user.aw
    go_home_recommend(aw)
    if not aw.accessibility_exists(SB.KEY_BOTTOM_PLAYER):
        print("[skip] 首页无 bottom_player（无播放任务），播放页不可达，跳过本 stage")
        return
    assert aw.click_accessibility(SB.KEY_BOTTOM_PLAYER), "点底部播放条失败"
    assert aw.wait_accessibility(SB.KEY_FULL_PLAYER_PAGE, timeout=10), "未进入播放页"
    time.sleep(2.0)
    dump_nodes(aw, "player", y_max=340)
    shot(aw, "src_player.png")

    # 切换设备弹层（⛔ 只截标题行，禁止点设备行）
    if aw.accessibility_exists("player_device_button"):
        assert aw.click_accessibility("player_device_button"), "点设备切换按钮失败"
        assert aw.wait_accessibility("multiroom_sheet", timeout=10), "切换设备弹层未出现"
        time.sleep(1.5)
        dump_all(aw, "device_sheet")
        shot(aw, "src_device_sheet.png")
        aw.press_back()  # 关弹层
        time.sleep(1.5)
    else:
        print("[skip] 播放页无 player_device_button")

    # 收起播放页回首页
    assert aw.click_accessibility(SB.KEY_PLAYER_DISMISS_BUTTON), "点播放页收起失败"
    time.sleep(1.5)
    print("[stage player] done，已回首页")


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    stages = {
        "state": stage_state,
        "playlist": stage_playlist,
        "favorite_history": stage_favorite_history,
        "ai_chat": stage_ai_chat,
        "player": stage_player,
    }
    if stage not in stages:
        raise SystemExit(f"未知 stage: {stage!r}（可选 {' / '.join(stages)}）")
    stages[stage]()
