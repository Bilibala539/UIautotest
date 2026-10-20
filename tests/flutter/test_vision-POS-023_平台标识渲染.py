# CASE-ID: vision-POS-023
# LINKED-CASE: vision-POS-023
"""Swan 回归·M10 可视音箱 Vision：编辑器平台标识按平台类型渲染——Qobuz=22 锚点（vision-POS-023）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- S1 进入方案编辑器并定位平台标识区 → ensure_logged_in_on_home
  + go_top_tab('可视音箱') + open_vision_advanced_settings
  + open_vision_scheme_editor('Qobuz')（terraceType=22 测试锚点平台分组卡）
- S2 Qobuz 标识渲染 → text_exists('Qobuz')（logo 与平台名对应——logo 图形
  断言归模板标定，见 package_report.template_needs；OCR 平台名为本用例判据）
- S3 其他平台 logo 一一对应 → 环境平台集合相关，收口于 Qobuz 锚点正向，
  无 logo 错挂的全量核对归 explorer 补测
前置：编辑器可选平台含 Qobuz（terraceType=22）及其他平台（环境预置）。
清理：只读浏览零写；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionPlatformLogo(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """编辑器平台标识按平台类型渲染——Qobuz=22 锚点（vision-POS-023）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_platform_logo_qobuz_anchor(self):
        """Qobuz 编辑器落地、平台标识区渲染（Qobuz 锚点）；退出零写。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_advanced_settings()
        # S1 进入 Qobuz（terraceType=22）编辑器
        self.userA.open_vision_scheme_editor('Qobuz')
        # S2 平台标识渲染（Qobuz 平台名 OCR 锚）
        self.userA.text_exists('Qobuz', timeout=10)
        # S3 退出（只读）
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
