# CASE-ID: music-POS-026
"""Swan 回归·M07 酷狗:电台分类页主路径(music-POS-026,内容页行为归 M08)。

步骤→AW 映射(/music_platform/kugou/radio-classify):
  1. 酷狗主页点电台分类入口 → open_platform_home('kugou') +
     scroll_to_text('电台') + click_text('电台') → 电台分类页打开
  2. 分类内容渲染(只验页面挂载) → assert_any_text(['电台','分类'])
     (变体锚 B 口径)

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:酷狗主页无知识库页面档案(全站未探索),入口/落页锚为变体
B 口径;页面专属锚真机补截后收紧
(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos026KugouRadioClassify(BaseTest):
    """酷狗电台分类页主路径可达,分类内容渲染正常。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_kugou_radio_classify(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:酷狗主页 → 电台分类入口
        self.userA.open_platform_home("kugou")
        self.userA.scroll_to_text("电台")
        self.userA.click_text("电台", timeout=8)
        # 步骤 2:分类内容渲染(只验页面挂载)
        self.userA.assert_any_text(["电台", "分类"])
