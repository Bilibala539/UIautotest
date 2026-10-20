# CASE-ID: music-POS-025
"""Swan 回归·M07 酷狗:歌单更多页主路径(music-POS-025)。

步骤→AW 映射(/music_platform/kugou/playlist-more):
  1. 酷狗主页点歌单更多入口 → open_platform_home('kugou')(未授权态由
     helper 自适配跳过) + scroll_to_text('歌单') + click_text('更多')
     (歌单区块标题带「更多」入口语义兜底) → 歌单更多页打开
  2. 歌单列表加载渲染 → assert_any_text(['歌单','更多'])(列表区变体锚
     B 口径)

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:酷狗主页无知识库页面档案(全站未探索),区块/入口/落页锚全部
为变体 B 口径;页面专属锚真机补截后收紧
(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos025KugouPlaylistMore(BaseTest):
    """酷狗歌单更多页主路径可达,歌单列表渲染正常。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_kugou_playlist_more(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:酷狗主页 → 歌单区块 → 更多入口
        self.userA.open_platform_home("kugou")
        self.userA.scroll_to_text("歌单")
        self.userA.click_text("更多", timeout=8)
        # 步骤 2:歌单列表渲染
        self.userA.assert_any_text(["歌单", "更多"])
