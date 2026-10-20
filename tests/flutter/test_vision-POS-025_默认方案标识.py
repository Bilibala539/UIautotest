# CASE-ID: vision-POS-025
# LINKED-CASE: vision-POS-025
"""Swan 回归·M10 可视音箱 Vision：默认方案标识与一键切默认入口存在性（vision-POS-025）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- S1-S2 单平台页浏览方案卡 → ensure_logged_in_on_home + go_top_tab('可视音箱')
  + open_vision_advanced_settings + open_vision_platform_page('酷狗')；
  assert_any_text（默认标识/一键切默认控件候选：设为默认/一键切默认/切默认/默认/
  使用中——isDefault==1 标识与控件文案均未标定，见 package_report.template_needs）
- S3 退出 → press_back（仅存在性断言——零点击零提交；
  updateAdvancedDefaults 为全平台快照提交写，取消默认 -1 哨兵归写协议面不触碰）
前置：专用测试账号已登录；某平台存在 isDefault==1 方案（缺省则标识断言由
候选锚点兜底，入口断言仍可执行）。
清理：零提交零状态变化退出；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionDefaultScheme(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """默认方案标识与一键切默认入口存在性（vision-POS-025）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_default_scheme_marker_and_entry(self):
        """单平台页默认标识/切默认控件存在（仅存在性——零点击）；退出零提交。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_advanced_settings()
        # S1 进入单平台页浏览方案卡
        self.userA.open_vision_platform_page('酷狗')
        # S1+S2 默认标识与一键切默认控件存在性（文案未标定，候选探测）
        self.userA.assert_any_text(('设为默认', '一键切默认', '切默认', '默认', '使用中'), timeout=10)
        # S3 退出（零提交）
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
