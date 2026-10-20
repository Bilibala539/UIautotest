# CASE-ID: profile-POS-034
"""Swan 回归·M13 个人中心：Tab 切换滚动位置保持（profile-POS-034）。

用例 → AW 映射（A- 级）：
- 我的页滚动到底（「关于与升级」可见）→ me_row_scroll_until
- 切首页再切回我的 → go_bottom_tab（内建到位断言）
- 滚动位置保持：切回后「关于与升级」立即可见（text_exists 无需滚动）
- （若位置被重置则该行不可见，断言失败=状态保持缺陷暴露）
清理（G3/G4）：只读断言无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos034TabSwitchStateKept(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_tab_switch_state_kept(self) -> None:
        self.userA.open_me_page()
        # 滚动到底：关于与升级可见
        self.userA.me_row_scroll_until("关于与升级")
        # 切首页再切回我的
        self.userA.go_bottom_tab("首页")
        self.userA.go_bottom_tab("我的")
        # 滚动位置保持：关于与升级立即可见
        self.userA.text_exists("关于与升级", timeout=5)

    def teardown(self) -> None:
        pass
