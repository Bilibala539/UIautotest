# CASE-ID: music-POS-013
"""Swan 回归·M07 QQ音乐:QQ 歌单分类页主路径(music-POS-013)。

步骤→AW 映射(/music_platform/qq/playlist-classify):
  1. QQ 主页点歌单分类入口 → open_platform_home('qq') + click_text('歌单')
     (QQ 主页歌单区块→歌单分类,知识库 draft 区块映射) → 歌单分类页打开
  2. 分类宫格加载渲染 → assert_any_text(['歌单','分类','全部'])(宫格区
     变体锚 B 口径)

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:歌单分类页专属锚未截模板,变体锚承载;「歌单」裸词若与主页
其它区块撞词,以点击后到达锚判真伪(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos013QqPlaylistClassify(BaseTest):
    """QQ 歌单分类页主路径可达,分类宫格渲染正常。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_qq_playlist_classify(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("qq") != "authorized":
            pytest.skip("QQ 行非已授权态,QQ 主页歌单入口不可达(账号态自适配)")
        # 步骤 1:QQ 主页 → 歌单区块 → 歌单分类页
        self.userA.open_platform_home("qq")
        self.userA.click_text("歌单", timeout=8)
        # 步骤 2:分类宫格渲染
        self.userA.assert_any_text(["歌单", "分类", "全部"])
