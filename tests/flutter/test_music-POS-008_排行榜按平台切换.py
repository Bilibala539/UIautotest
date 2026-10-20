# CASE-ID: music-POS-008
"""Swan 回归·M07 平台通用:排行榜按平台入口切换(default=qq)(music-POS-008)。

步骤→AW 映射(PlatformRankListArgs 来源平台参数契约,别名 default 落 qq):
  1. QQ 主页点「排行榜」入口 → open_platform_home('qq') + click_text('排行榜'),
     rank-list 打开且平台为 QQ → assert_any_text(['飙升榜','榜单','排行榜'])
  2. 返回后进网易云主页点「排行榜」入口 → go_bottom_tab('平台') +
     open_platform_home('netease')(网易云已授权为环境常态) + click_text
     ('排行榜')(网易云实测落排行榜聚合页),平台为网易云 → 变体锚核对
  3. 榜单组横向切换(组间导航) → swipe_left() 后页面仍渲染(无空屏无崩溃)

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:rank-list 页「平台归属」无专属文案锚,以榜单变体锚 B 口径承载;
「榜单平台为 QQ/网易云」的精确断言需页面专属锚真机补截后收紧
(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos008RankListPlatformSwitch(BaseTest):
    """排行榜按来源平台参数渲染,组间横向切换正常。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_rank_list_platform_switch(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("qq") != "authorized":
            pytest.skip("QQ 行非已授权态,QQ 主页排行榜入口不可达(账号态自适配)")
        # 步骤 1:QQ 来源 rank-list
        self.userA.open_platform_home("qq")
        self.userA.click_text("排行榜", timeout=8)
        self.userA.assert_any_text(["飙升榜", "榜单", "排行榜"])
        # 步骤 2:网易云来源 rank-list(网易云已授权为环境常态)
        self.userA.go_bottom_tab("平台")
        self.userA.open_platform_home("netease")
        self.userA.click_text("排行榜", timeout=8)
        self.userA.assert_any_text(["排行榜", "榜单", "网易云"])
        # 步骤 3:榜单组横向切换,组间导航渲染无空屏
        self.userA.swipe_left()
        self.userA.assert_any_text(["飙升榜", "榜单", "排行榜"])
