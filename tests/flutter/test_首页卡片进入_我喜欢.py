"""Swan 回归·导航域：首页推荐 Tab 卡片进入对应页面（回归用例 31）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域4）：
- 用例31 首页推荐 Tab 卡片进入对应页面 → open_home_card(name) [OCR]
  （支持 我喜欢/歌单/最近播放族；AI/个性化推荐卡落的页 KB 未探索不支持）

已知陷阱（知识库）：推荐 Tab 完整/紧凑布局轮换——由业务方法内部处理
（歌单卡未找到时下拉刷新重试）。
rig 环境变量与公共前置/清理见 utils/aw/business/swan_regression.py。
清理（G3/G4）：收播放页 → 退出 push 页 → go_home（mixin teardown）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanContentRegressionMixin


HOME_CARDS = ["我喜欢", "歌单", "最近播放"]


class TestHomeCardEntry(SwanContentRegressionMixin, BaseTest):
    """首页推荐 Tab 卡片进入对应页面（回归用例 31）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_home_card_entry(self):
        """用例31：首页推荐 Tab 卡片进入对应页面（卡片 OCR 定位）。"""
        card = '我喜欢'
        self._ensure_logged_in_on_home()
        self.userA.open_home_card(card)

    def teardown(self) -> None:
        """G3/G4 清理链由 mixin teardown 承担（本用例无自定义清理）。"""
        super().teardown()