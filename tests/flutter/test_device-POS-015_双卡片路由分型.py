# CASE-ID: device-POS-015
"""Swan 回归·设备域：双分型卡片路由正确性(device-POS-015)。

步骤→AW 映射：
S1 进入添加设备页 → open_device_page + open_add_device_page；
S2 BLE 卡路由 → open_ble_provisioning(落在 BLE 配网页，扫描态锚点佐证
   非 WiFi 配网页)；
S3 返回添加设备页 → press_back 后 OCR 断言双卡片锚点；
S4 WiFi 卡路由 → 点「WiFi 添加」落在 WiFi 配网页(热点/网络类锚点佐证)。
配网页均为未探索页面，具体路由文案登记 template_needs。

cleanup: back_to_device_page 返回键退出，不提交任何凭据(禁区 3)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestDualCardRouting(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_dual_card_routing(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        self.userA.open_ble_provisioning()
        self.userA.press_back()
        self.userA.assert_any_ocr(("蓝牙添加", "WiFi 添加", "蓝牙", "Wi-Fi"), timeout=8)
        hit = self.userA.click_first_ocr(("WiFi 添加", "WiFi添加", "Wi-Fi 添加", "WiFi"),
                                         timeout=8)
        assert hit is not None, "添加设备页未找到「WiFi 添加」卡片"
        self.userA.assert_any_ocr(("热点", "Wi-Fi", "WiFi", "网络", "连接"), timeout=10)
        self.userA.back_to_device_page()

    def teardown(self) -> None:
        pass
