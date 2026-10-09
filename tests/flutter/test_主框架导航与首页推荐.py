"""Swan 回归·导航域：主框架导航与首页推荐（回归用例 29-31）。

用例 -> AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域4）：
- 用例29 底部四 Tab 轮巡（首页/平台/设备/我的）-> go_bottom_tab(name)，
  逐页一级锚点 [图] 断言（底部导航图标为域4 新截草稿，PNG 未截前该组
  用例因模板缺失失败，属预期状态）
- 用例30 首页五顶 Tab 切换（推荐/音乐/AI/可视音箱/电台）-> go_top_tab(name)，
  逐 Tab 页面锚点 [图] 断言（顶 Tab 5 张已转正图）
- 用例31 首页推荐 Tab 卡片进入对应页面 -> open_home_card(name) [OCR]
  （支持 我喜欢/歌单/最近播放族；AI/个性化推荐卡落的页 KB 未探索不支持）

已知陷阱（知识库）：顶 Tab 持久化、推荐 Tab 完整/紧凑布局轮换——
均由业务方法内部处理（显式点顶 Tab / 歌单卡未找到时下拉刷新重试）。
清理（G3/G4）：SwanContentRegressionMixin.teardown——收播放页 ->
退出 push 页 -> go_home（key 导航迁移待拍板例外）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from tests.flutter.swan_regression_common2 import SwanContentRegressionMixin

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone,
    reason="Swan 用例需要 PLATFORM=flutter 和 SWAN_PHONE",
)

BOTTOM_TABS = ["首页", "平台", "设备", "我的"]
TOP_TABS = ["推荐", "音乐", "AI", "可视音箱", "电台"]
HOME_CARDS = ["我喜欢", "歌单", "最近播放"]


class TestNavigationAndHome(SwanContentRegressionMixin, BaseTest):
    """主框架导航与首页推荐（回归用例 29-31）。"""

    @pytest.mark.parametrize("tab", BOTTOM_TABS)
    def test_bottom_tab_switch(self, tab):
        """用例29：底部四 Tab 轮巡，逐页一级锚点 [图] 断言。"""
        self._ensure_logged_in_on_home()
        if tab == "首页":
            self.user.go_bottom_tab("平台")  # 先离开首页再切回，避免短路空转
        self.user.go_bottom_tab(tab)

    @pytest.mark.parametrize("tab", TOP_TABS)
    def test_top_tab_switch(self, tab):
        """用例30：首页五顶 Tab 切换，逐 Tab 页面锚点 [图] 断言。"""
        self._ensure_logged_in_on_home()
        self.user.go_top_tab(tab)

    @pytest.mark.parametrize("card", HOME_CARDS)
    def test_home_card_entry(self, card):
        """用例31：首页推荐 Tab 卡片进入对应页面（卡片 OCR 定位）。"""
        self._ensure_logged_in_on_home()
        self.user.open_home_card(card)
