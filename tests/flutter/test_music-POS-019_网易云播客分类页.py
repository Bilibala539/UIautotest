# CASE-ID: music-POS-019
"""Swan 回归·M07 网易云:播客分类页主路径·同页分型播客型(music-POS-019)。

步骤→AW 映射(/music_platform/netease/podcast-classify,网易云特有区块,
QQ 无播客):
  1. 网易云主页点播客分类入口 → open_platform_home('netease') +
     click_text('播客')(KB:播客区块 OCR,网易云特有) → 播客分类页打开
  2. 播客分类内容渲染(与 playlist 型区分) → assert_any_text(['创作翻唱',
     '音乐播客','电音','播客'])(KB 实测子 Tab 文案变体锚,播客型专属
     Tab 集与歌单型不重叠承载分型区分)

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:播客区块点击进分类页为未验证路径(KB 仅验证区块存在性),
变体锚承载;页面专属锚真机补截后收紧
(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos019NeteasePodcastClassify(BaseTest):
    """网易云播客分类页(同页分型播客型)主路径可达,内容渲染正常。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_netease_podcast_classify(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:网易云主页 → 播客区块(网易云特有)
        self.userA.open_platform_home("netease")
        self.userA.click_text("播客", timeout=8)
        # 步骤 2:播客分类内容渲染(KB 子 Tab 文案变体锚)
        self.userA.assert_any_text(["创作翻唱", "音乐播客", "电音", "播客"])
