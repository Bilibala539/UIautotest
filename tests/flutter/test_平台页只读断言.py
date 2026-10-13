# CASE-ID: aw-平台页只读断言
"""Swan Flutter 平台页只读断言（原 test_swan_readonly_pages.py，2026-10-12 拆分）。

前置：账号已登录（用例开头 login_by_sms 幂等确保，已在首页自动跳过）。

⛔ 危险入口一律不点（只做存在性断言）：授权/充值（netease_platform_entry
等"+"按钮）。
断言优先级：图片（image_exists）> OCR；2026-10-12 起 key 已全部迁移。
断言辅助与锚点探测在 SwanLoginRegressionMixin（业务层）。
每条用例收尾回首页（G3/G4）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_PLATFORM_NETEASE_ROW,
    SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED,
    SWAN_TAB_PLATFORM,
)
from utils.aw.business.swan_regression import SwanLoginRegressionMixin



class TestSwanPlatformPageReadonly(SwanLoginRegressionMixin, BaseTest):
    """平台页只读断言。"""

    def setup(self) -> None:
        """pytest 生命周期钩子（模板要求显式声明；逻辑由 mixin 提供）。"""
        super().setup()

    def test_platform_page_readonly(self):
        """平台页只读断言：根节点 + 网易云行 key + 行图片；⛔ 不点授权/充值。"""
        self._ensure_logged_in_on_home()
        # 2026-10-12 key 迁移：SWAN_TAB_PLATFORM [图] 点击（未选中态），
        # 到位断言用平台页特有锚——网易云行两态 [图]（行卡渲染随账号授权态
        # 切换：未授权白底+「未授权」/已授权黄底+昵称，两态模板成对，同协议
        # 勾选框先例），任一命中即"已到平台页且网易云行存在"
        self.aw.click_image(SWAN_TAB_PLATFORM, timeout=10)
        row_visible = (
            self.aw.find_image(SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED, timeout=8)
            is not None
            or self.aw.find_image(SWAN_PLATFORM_NETEASE_ROW, timeout=8) is not None
        )
        assert row_visible, (
            "平台页网易云行两态 [图] 均未命中（未到达平台页？或模板与账号"
            "授权态不匹配，请核对两态模板登记）")
        self.user.go_home()

    def teardown(self) -> None:
        """G3/G4 清理链由 mixin teardown 承担（本用例无自定义清理）。"""
        super().teardown()