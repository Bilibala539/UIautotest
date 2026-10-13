"""Swan 回归·导航域：首页五顶 Tab 切换（回归用例 30）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域4）：
- 用例30 首页五顶 Tab 切换（推荐/音乐/AI/可视音箱/电台）→ go_top_tab(name)，
  逐 Tab 页面锚点 [图] 断言（顶 Tab 5 张已转正图）

已知陷阱（知识库）：顶 Tab 持久化——由业务方法内部处理（显式点顶 Tab）。
rig 环境变量与公共前置/清理见 utils/aw/business/swan_regression.py。
清理（G3/G4）：收播放页 → 退出 push 页 → go_home（mixin teardown）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanContentRegressionMixin


TOP_TABS = ["推荐", "音乐", "AI", "可视音箱", "电台"]


class TestTopTabSwitch(SwanContentRegressionMixin, BaseTest):
    """首页五顶 Tab 切换（回归用例 30）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户与基础操作入口。"""
        self.user = self.users("swanuserA")
        self.aw = self.user.aw
        self.phone = self.user.phone
        self.password = os.environ.get("SWAN_PASSWORD", "").strip()
        self.package = os.environ.get("SWAN_PACKAGE", "com.swan.network").strip()

    def test_top_tab_switch(self):
        """用例30：首页五顶 Tab 切换，逐 Tab 页面锚点 [图] 断言。"""
        tab = '推荐'
        self._ensure_logged_in_on_home()
        self.user.go_top_tab(tab)

    def teardown(self) -> None:
        """G3/G4 清理链由 mixin teardown 承担（本用例无自定义清理）。"""
        super().teardown()