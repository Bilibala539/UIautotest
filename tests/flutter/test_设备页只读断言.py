"""Swan Flutter 设备页只读断言（原 test_swan_readonly_pages.py，2026-10-12 拆分）。

前置：账号已登录（用例开头 login_by_sms 幂等确保，已在首页自动跳过）。

⛔ 危险入口一律不点（只做存在性断言）：设备卡/设置/同步/音量设置/添加设备。
断言辅助与锚点探测在 SwanLoginRegressionMixin（业务层，存量 key 口径）。
每条用例收尾回首页（G3/G4）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_DEVICE_ADD_BTN, SWAN_TAB_DEVICE
from utils.aw.business.swan import SwanBusiness  # 仅用 PREFIX_* 常量（探索辅助豁免候选，待拍板）
from utils.aw.business.swan_regression import SwanLoginRegressionMixin

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone,
    reason="Swan 用例需要 PLATFORM=flutter 和 SWAN_PHONE",
)


class TestSwanDevicePageReadonly(SwanLoginRegressionMixin, BaseTest):
    """设备页只读断言。"""

    def test_device_page_elements(self):
        """设备页只读断言：根节点 + 添加设备（key+图片）+ 设备卡前缀匹配 ≥1 台。

        设备卡 key 按 UUID 动态拼接（wifi_device_card_<UUID>），用前缀遍历
        dump 判断，不写死 UUID。⛔ 不点设备卡/同步/音量/添加设备。
        """
        self._ensure_logged_in_on_home()
        # 2026-10-12 key 迁移：SWAN_TAB_DEVICE [图] 点击，到位断言用
        # 设备页特有锚 SWAN_DEVICE_ADD_BTN [图]（key+图片双校验合并为图）
        self.aw.click_image(SWAN_TAB_DEVICE, timeout=10)
        self.aw.image_exists(SWAN_DEVICE_ADD_BTN, timeout=15)
        card_keys = self.aw.list_accessibility_keys_by_prefix(
            SwanBusiness.PREFIX_WIFI_DEVICE_CARD
        )
        assert card_keys, (
            "设备页未发现任何 WIFI 设备卡（wifi_device_card_* 为空）。"
            "若页面显示「暂无WIFI设备」，说明账号当前未绑定设备（数据状态变化，"
            "非代码问题），需先在真机上重新配网绑定设备后再跑本用例"
        )
        self.user.go_home()
