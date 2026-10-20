# CASE-ID: music-POS-020
"""Swan 回归·M07 网易云:歌单全部分类页主路径(music-POS-020)。

步骤→AW 映射(/music_platform/netease/playlist-all-classify):
  1. 网易云歌单分类页进全部 → open_platform_home('netease') + click_text
     ('歌单', region=(0, 300, 160, 1312))(裸词坑 region 口径,KB 10-12 实测)
     → find_text_by_ocr('全部') 探测 → click_text('全部') → 全部分类页
  2. 全量分类加载渲染 → assert_any_text(['歌单','分类'])(列表区变体锚
     B 口径)

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:「全部」入口在网易云歌单分类页的实际文案形态未截模板(KB 仅
验证子 Tab 行),探测式点击;页面专属锚真机补截后收紧
(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos020NeteasePlaylistAllClass(BaseTest):
    """网易云歌单全部分类页主路径可达,全量分类渲染正常。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_netease_playlist_all_classify(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:网易云主页 → 歌单分类页 → 全部
        self.userA.open_platform_home("netease")
        self.userA.click_text("歌单", timeout=8, region=(0, 300, 160, 1312))
        assert self.userA.find_text_by_ocr("全部", timeout=10) is not None, (
            "歌单分类页未出现「全部」入口(未达分类页或文案变体)")
        self.userA.click_text("全部", timeout=5)
        # 步骤 2:全量分类渲染
        self.userA.assert_any_text(["歌单", "分类"])
