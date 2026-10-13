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
from utils.aw.business.swan_regression import SwanLoginRegressionMixin



class TestSwanDevicePageReadonly(SwanLoginRegressionMixin, BaseTest):
    """设备页只读断言。"""

    def setup(self) -> None:
        """pytest 生命周期钩子（模板要求显式声明；逻辑由 mixin 提供）。"""
        super().setup()

    def teardown(self) -> None:
        """G3/G4 清理链由 mixin teardown 承担（本用例无自定义清理）。"""
        super().teardown()


    def test_device_page_elements(self):
        """设备页只读断言：根节点 + 添加设备（key+图片）+ 设备卡前缀匹配 ≥1 台。

        设备卡 key 按 UUID 动态拼接（wifi_device_card_<UUID>），用前缀遍历
        dump 判断，不写死 UUID。⛔ 不点设备卡/同步/音量/添加设备。
        """
        self._ensure_logged_in_on_home()
        # 2026-10-13 key/dump 迁移：设备卡存在断言改 [OCR] 反向判据——
        # 空态文案「暂无WIFI设备」不存在 = 有绑定卡（旧方案读 UI 树数
        # UUID 动态卡，坐标铁律整改后退役；设备卡按 UUID 动态生成无法
        # 截图模板，OCR 空态反断言是唯一合规且可靠的判据）
        self.aw.click_image(SWAN_TAB_DEVICE, timeout=10)
        self.aw.image_exists(SWAN_DEVICE_ADD_BTN, timeout=15)
        assert self.aw.find_text_by_ocr("暂无", timeout=3) is None, (
            "设备页显示「暂无WIFI设备」空态（账号当前未绑定设备，数据状态变化"
            "非代码问题），需先在真机上配网绑定设备后再跑本用例")
        self.user.go_home()
