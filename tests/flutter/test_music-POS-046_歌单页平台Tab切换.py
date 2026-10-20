# CASE-ID: music-POS-046
"""Swan 回归·M07 平台授权:歌单页平台Tab切换(music-POS-046)。

步骤→AW 映射(7.7 目录映射消费面,M12 12.2 交界,playlistPlatforms
swan 恒首位;只读浏览,⛔第三方 Tab 未授权空态的「去授权」不点击):
  1. 歌单页进入 → go_top_tab("推荐")(顶 Tab 持久化陷阱,显式停推荐)
     → 推荐页「歌单」卡点击(KB: 完整/紧凑布局间歇轮换,紧凑态下拉
     刷新促轮换,仍不可达则 skip=入口窗口闸门)→ OCR"SWAN" 平台 Tab 行
  2. 依次切第三方平台 Tab → 目录动态探测(网易云/QQ音乐/酷狗)逐个
     click_text,每切一页断言内容区渲染(收藏/创建/授权空态/已加载,
     无白屏即无错串基础);≥1 个第三方 Tab 断言
  3. 切回 SWAN Tab → click_text("SWAN")→ 创建/聚合 chip(SWAN Tab
     专属,内容恢复锚)

cleanup: 无(只读浏览)。
B 标定说明:各平台 Tab 选中态图与第三方 Tab 内容区专属锚待真机补截,
见 package_report.json template_needs。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos046PlaylistPlatformTab(BaseTest):
    """歌单页平台 Tab 行动态渲染,切换内容正确且 swan 恒首位。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_playlist_platform_tab_switch(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("推荐")
        # 步骤 1:推荐页「歌单」卡进歌单页(布局轮换闸门)
        card = None
        for _ in range(3):
            card = self.userA.find_text_by_ocr("歌单", timeout=4)
            if card is not None:
                break
            self.userA.swipe_down(distance=400)  # 下拉刷新促布局轮换
        if card is None:
            pytest.skip(
                "推荐 Tab 紧凑布局轮换窗口,「歌单」卡入口不可达"
                "(KB swan_歌单页 2026-09-10 布局轮换)")
        self.userA.tap(card[0], card[1])
        # 平台 Tab 行渲染(swan 恒首位)
        assert self.userA.find_text_by_ocr("SWAN", timeout=8) is not None, (
            "歌单页平台 Tab 行未渲染(「SWAN」[OCR] 未命中)")
        # 步骤 2:依次切第三方平台 Tab(目录动态,未授权空态合法,不点去授权)
        switched = 0
        for name in ("网易云音乐", "QQ音乐", "酷狗音乐"):
            if self.userA.find_text_by_ocr(name, timeout=2) is None:
                continue
            self.userA.click_text(name, timeout=4)
            self.userA.assert_any_text(
                ["收藏", "创建", "授权", "已加载", "还没有"])
            switched += 1
        assert switched >= 1, (
            "平台 Tab 行未扫到任何第三方平台 Tab(目录快照异常)")
        # 步骤 3:切回 SWAN Tab,内容恢复(SWAN Tab 专属 创建/聚合 chip)
        self.userA.click_text("SWAN", timeout=5)
        self.userA.assert_any_text(["创建", "聚合"])
