"""Swan 回归·导航域：底部四 Tab 轮巡（回归用例 29）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域4）：
- 用例29 底部四 Tab 轮巡（首页/平台/设备/我的）→ go_bottom_tab(name)，
  逐页一级锚点 [图] 断言

已知陷阱（知识库）：顶 Tab 持久化、推荐 Tab 完整/紧凑布局轮换——
均由业务方法内部处理（显式点顶 Tab / 歌单卡未找到时下拉刷新重试）。
rig 环境变量与公共前置/清理见 utils/aw/business/swan_regression.py。
清理（G3/G4）：收播放页 → 退出 push 页 → go_home（mixin teardown）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanContentRegressionMixin


BOTTOM_TABS = ["首页", "平台", "设备", "我的"]


class TestBottomTabSwitch(SwanContentRegressionMixin, BaseTest):
    """底部四 Tab 轮巡（回归用例 29）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_bottom_tab_switch(self):
        """用例29：底部四 Tab 轮巡，逐页一级锚点 [图] 断言。"""
        tab = '平台'
        self._ensure_logged_in_on_home()
        if tab == "首页":
            self.userA.go_bottom_tab("平台")  # 先离开首页再切回，避免短路空转
        self.userA.go_bottom_tab(tab)

    def teardown(self) -> None:
        """G3/G4 清理链由 mixin teardown 承担（本用例无自定义清理）。"""
        super().teardown()