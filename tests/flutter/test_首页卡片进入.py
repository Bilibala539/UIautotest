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

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone,
    reason="Swan 用例需要 PLATFORM=flutter 和 SWAN_PHONE",
)

HOME_CARDS = ["我喜欢", "歌单", "最近播放"]


class TestHomeCardEntry(SwanContentRegressionMixin, BaseTest):
    """首页推荐 Tab 卡片进入对应页面（回归用例 31）。"""

    @pytest.mark.parametrize("card", HOME_CARDS)
    def test_home_card_entry(self, card):
        """用例31：首页推荐 Tab 卡片进入对应页面（卡片 OCR 定位）。"""
        self._ensure_logged_in_on_home()
        self.user.open_home_card(card)
