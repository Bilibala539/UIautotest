# CASE-ID: music-POS-015
"""Swan 回归·M07 QQ音乐:QQ 歌单全部分类页主路径(music-POS-015)。

步骤→AW 映射(/music_platform/qq/playlist-all-classify):
  1. QQ 歌单分类页进全部分类 → open_platform_home('qq') + click_text('歌单')
     → click_text('全部')(分类宫格首项) → 全部分类页打开
  2. 全量分类列表加载渲染 → assert_any_text(['歌单','分类'])(列表区变体
     锚 B 口径)

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:全部分类页专属锚未截模板,变体锚承载;「全部」入口在宫格中的
实际文案形态(全部/全部歌单)真机标定后收紧
(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos015QqPlaylistAllClass(BaseTest):
    """QQ 歌单全部分类页主路径可达,全量分类列表渲染正常。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_qq_playlist_all_classify(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("qq") != "authorized":
            pytest.skip("QQ 行非已授权态,QQ 主页歌单入口不可达(账号态自适配)")
        # 步骤 1:QQ 主页 → 歌单分类页 → 全部分类
        self.userA.open_platform_home("qq")
        self.userA.click_text("歌单", timeout=8)
        assert self.userA.find_text_by_ocr("全部", timeout=10) is not None, (
            "歌单分类页未出现「全部」入口(宫格未渲染或文案变体)")
        self.userA.click_text("全部", timeout=5)
        # 步骤 2:全量分类列表渲染
        self.userA.assert_any_text(["歌单", "分类"])
