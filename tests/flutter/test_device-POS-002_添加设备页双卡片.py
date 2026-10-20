# CASE-ID: device-POS-002
"""Swan 回归·设备域：添加设备页双分型卡片(device-POS-002)。

步骤→AW 映射：
S1 添加入口 → open_device_page + open_add_device_page(右上角添加设备[图])；
S2 BLE 卡片 → OCR 断言「蓝牙添加」文案；
S3 WiFi 卡片 → OCR 多候选断言「WiFi 添加」(空格变体容忍)。
添加设备页为未探索页面(无已注册模板)，卡片文案以 YAML 为准登记 template_needs。

cleanup: back_to_device_page 返回键退出，无状态变更。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestAddDevicePageDualCards(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_add_device_page_dual_cards(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        self.userA.open_add_device_page()
        self.userA.assert_any_ocr(("蓝牙添加",), timeout=8)
        self.userA.assert_any_ocr(("WiFi 添加", "WiFi添加", "Wi-Fi 添加"), timeout=8)
        self.userA.back_to_device_page()

    def teardown(self) -> None:
        pass
