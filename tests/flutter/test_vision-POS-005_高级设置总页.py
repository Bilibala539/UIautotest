# CASE-ID: vision-POS-005
# LINKED-CASE: vision-POS-005
"""Swan 回归·M10 可视音箱 Vision：高级设置总页可达与平台分组渲染（vision-POS-005）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- S1 进入高级设置 → ensure_logged_in_on_home + go_top_tab('可视音箱')
  + open_vision_advanced_settings（入口 OCR「高级设置」→ 落地锚）
- S2 平台分组方案卡渲染 → assert_any_text（「方案」/「高级设置」锚）+ swipe_up 遍历
- S3 返回退出 → press_back（回 Vision 页）
前置：已绑定 MG100 TESTDEV-MG100-01 在线（Vision 入口依赖）。
清理：只读浏览零写；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionAdvancedHome(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """高级设置总页可达与平台分组渲染（vision-POS-005）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_advanced_settings_page_reachable(self):
        """高级设置总页落地、平台分组方案卡渲染无白屏；返回 Vision 页。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_advanced_settings()
        # S2 平台分组与方案卡渲染锚点
        self.userA.assert_any_text(('方案', '高级设置'), timeout=10)
        # S3 滚动遍历分组（无卡死）
        self.userA.swipe_up()
        # S3 返回退出
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
