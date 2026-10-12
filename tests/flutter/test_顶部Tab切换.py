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

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone,
    reason="Swan 用例需要 PLATFORM=flutter 和 SWAN_PHONE",
)

TOP_TABS = ["推荐", "音乐", "AI", "可视音箱", "电台"]


class TestTopTabSwitch(SwanContentRegressionMixin, BaseTest):
    """首页五顶 Tab 切换（回归用例 30）。"""

    @pytest.mark.parametrize("tab", TOP_TABS)
    def test_top_tab_switch(self, tab):
        """用例30：首页五顶 Tab 切换，逐 Tab 页面锚点 [图] 断言。"""
        self._ensure_logged_in_on_home()
        self.user.go_top_tab(tab)
