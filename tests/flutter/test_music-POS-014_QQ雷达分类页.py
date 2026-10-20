# CASE-ID: music-POS-014
"""Swan 回归·M07 QQ音乐:QQ 雷达分类页主路径(music-POS-014)。

步骤→AW 映射(/music_platform/qq/radar-classify):
  1. QQ 主页点雷达分类入口 → open_platform_home('qq') + scroll_to_text
     ('音乐雷达')(知识库 draft 区块) + click_text('音乐雷达') → 雷达
     分类页打开
  2. 雷达内容加载渲染 → assert_any_text(['雷达','推荐'])(内容变体锚
     B 口径)

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:雷达分类页专属锚未截模板,变体锚承载;页面专属锚真机补截后
收紧(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos014QqRadarClassify(BaseTest):
    """QQ 雷达分类页主路径可达,内容渲染正常。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_qq_radar_classify(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("qq") != "authorized":
            pytest.skip("QQ 行非已授权态,QQ 主页雷达入口不可达(账号态自适配)")
        # 步骤 1:QQ 主页 → 音乐雷达区块 → 雷达分类页
        self.userA.open_platform_home("qq")
        self.userA.scroll_to_text("音乐雷达")
        self.userA.click_text("音乐雷达", timeout=8)
        # 步骤 2:雷达内容渲染
        self.userA.assert_any_text(["雷达", "推荐"])
