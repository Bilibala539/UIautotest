# CASE-ID: music-POS-029
"""Swan 回归·M07 Qobuz:用户歌单页主路径(music-POS-029,需已授权账号)。

步骤→AW 映射(/music_platform/qobuz/user-playlists):
  1. Qobuz 主页点用户歌单入口 → open_platform_home('qobuz') + 入口变体
     探测('用户歌单'/'歌单')点击 → 用户歌单页打开
  2. 用户歌单数据加载(空态为合法态) → 页面锚存在性承载,不断言数据非空
  3. 无授权弹层误弹 → assert_no_auth_error()

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:Qobuz 主页无知识库档案,入口/落页锚为变体 B 口径;页面专属锚
真机补截后收紧(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos029QobuzUserPlaylist(BaseTest):
    """Qobuz 用户歌单页(已授权账号)主路径可用,无授权弹层误弹。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_qobuz_user_playlist(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:Qobuz 主页 → 用户歌单入口(变体探测)
        self.userA.open_platform_home("qobuz")
        entry = None
        for word in ("用户歌单", "歌单"):
            entry = self.userA.find_text_by_ocr(word, timeout=2)
            if entry is not None:
                break
        assert entry is not None, (
            "Qobuz 主页未扫到用户歌单入口(用户歌单/歌单变体均未命中;"
            "主页区块 [图] 模板待补截,见 package_report.json template_needs)")
        self.userA.tap(entry["cx"], entry["cy"])
        # 步骤 2:页面挂载(空态为合法态)
        self.userA.assert_any_text(["歌单", "播放"])
        self.userA.assert_no_auth_error()
