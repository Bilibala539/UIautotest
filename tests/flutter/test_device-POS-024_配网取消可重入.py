# CASE-ID: device-POS-024
"""Swan 回归·设备域：配网中途取消终止与重入(device-POS-024)。

步骤→AW 映射：
S1 BLE 卡进入配网页 → open_ble_provisioning(扫描自启，扫描态锚点)；
S2 扫描中返回退出 → press_back 离开配网页(扫描随页面退出终止)；
S3 重入验证状态干净 → 添加设备页双卡片锚点仍在，重进 BLE 配网页后
   assert_ble_scanning 扫描态重新建立(可重入，无残留)。

cleanup: back_to_device_page 返回键退出，不发生配对。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestProvisionCancelReentry(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_provision_cancel_and_reentry(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        self.userA.open_ble_provisioning()
        self.userA.press_back()
        self.userA.assert_any_ocr(("蓝牙添加", "WiFi 添加", "蓝牙", "Wi-Fi"), timeout=8)
        hit = self.userA.click_first_ocr(("蓝牙添加", "蓝牙"), timeout=6)
        assert hit is not None, "重进后添加设备页未找到「蓝牙添加」卡片(页面状态疑似残留)"
        self.userA.assert_ble_scanning()
        self.userA.back_to_device_page()

    def teardown(self) -> None:
        pass
