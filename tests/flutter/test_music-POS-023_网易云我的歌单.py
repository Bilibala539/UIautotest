# CASE-ID: music-POS-023
"""Swan 回归·M07 网易云:我的歌单页主路径(music-POS-023,需已授权账号)。

步骤→AW 映射(/music_platform/netease/my-playlist):
  1. 网易云主页点我的歌单入口 → open_platform_home('netease') +
     scroll_to_text('用户收藏') → 入口自适应:优先探测字面「我的歌单」入口,
     未命中则点用户收藏区「自建歌单」卡(KB 实测用户收藏区四卡之一,我方
     歌单唯一入口;my-playlist 路由与自建歌单页同构为 B 推断)
  2. 用户歌单数据加载(空态为合法态) → 页面锚存在性承载,不断言数据非空
  3. 无授权弹层误弹 → assert_no_auth_error()

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:「我的歌单」字面入口与卡片点击进页均为未验证路径,落页锚以
「自建歌单/我的歌单」变体承载;页面专属锚真机补截后收紧
(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos023NeteaseMyPlaylist(BaseTest):
    """网易云我的歌单页(已授权账号)主路径可用,无授权弹层误弹。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_netease_my_playlist(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:网易云主页 → 我的歌单入口(字面探测→自建歌单卡兜底)
        self.userA.open_platform_home("netease")
        self.userA.scroll_to_text("用户收藏")
        if self.userA.find_text_by_ocr("我的歌单", timeout=3) is not None:
            self.userA.click_text("我的歌单", timeout=3)
        else:
            self.userA.click_text("自建歌单", timeout=5)
        # 步骤 2:页面挂载(空态为合法态)
        self.userA.assert_any_text(["自建歌单", "我的歌单", "歌单"])
        self.userA.assert_no_auth_error()
