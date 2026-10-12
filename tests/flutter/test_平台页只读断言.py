"""Swan Flutter 平台页只读断言（原 test_swan_readonly_pages.py，2026-10-12 拆分）。

前置：账号已登录（用例开头 login_by_sms 幂等确保，已在首页自动跳过）。

⛔ 危险入口一律不点（只做存在性断言）：授权/充值（netease_platform_entry
等"+"按钮）。
断言优先级：图片（image_exists）> key（wait_accessibility）> OCR。
断言辅助与锚点探测在 SwanLoginRegressionMixin（业务层，存量 key 口径）。
每条用例收尾回首页（G3/G4）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_PLATFORM_NETEASE_ROW
from utils.aw.business.swan import SwanBusiness
from utils.aw.business.swan_regression import SwanLoginRegressionMixin

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone,
    reason="Swan 用例需要 PLATFORM=flutter 和 SWAN_PHONE",
)


class TestSwanPlatformPageReadonly(SwanLoginRegressionMixin, BaseTest):
    """平台页只读断言。"""

    def test_platform_page_readonly(self):
        """平台页只读断言：根节点 + 网易云行 key + 行图片；⛔ 不点授权/充值。"""
        self._ensure_logged_in_on_home()
        self.aw.click_accessibility(SwanBusiness.KEY_TAB_PLATFORM)
        assert self.aw.wait_accessibility(
            SwanBusiness.KEY_PLATFORM_PAGE, timeout=15
        ), "未进入平台页（platform_page 未出现）"
        assert self.aw.accessibility_exists(
            SwanBusiness.KEY_NETEASE_PLATFORM_ENTRY
        ), "平台页缺少网易云音乐行 key"
        self.aw.image_exists(SWAN_PLATFORM_NETEASE_ROW, timeout=10)
        self.user.go_home()
