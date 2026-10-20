# CASE-ID: vision-POS-019
# LINKED-CASE: vision-POS-019
"""Swan 回归·M10 可视音箱 Vision：高级设置总页平台分组方案卡浏览（vision-POS-019）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- S1 进入高级设置总页 → ensure_logged_in_on_home + go_top_tab('可视音箱')
  + open_vision_advanced_settings
- S2 平台分组方案卡渲染 → assert_any_text（「方案/高级设置」锚；getAdvancedList 正向）
- S3 滚动遍历全部分组 → swipe_up
- S4 退出 → press_back（一键切默认/新建/删除全不触碰——updateFacilityAdvanced/
  deleteAdvanced 均写，零写退出）
前置：已绑定 MG100 TESTDEV-MG100-01 在线或未绑定浏览态。
清理：零写退出；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionSchemeCards(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """高级设置总页平台分组方案卡浏览（vision-POS-019）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_browse_platform_group_scheme_cards(self):
        """总页落地、方案卡渲染、滚动遍历顺畅；零写退出。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_advanced_settings()
        # S2 平台分组与方案卡渲染锚点
        self.userA.assert_any_text(('方案', '高级设置'), timeout=10)
        # S3 滚动遍历全部分组
        self.userA.swipe_up()
        # S4 退出（零写）
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
